from banking.models import MultiSigTransaction
from banking.models import TransactionSignature
from eth_account.messages import encode_defunct
class MultiSigManager:
    def __init__(self, web3_client):
        self.web3_client = web3_client
    


    def create_multisig_transaction(self, transaction, required_signatures, expires_in_hours=24):
        """
        Create a multi-signature transaction that requires multiple approvals
        """
        from django.utils import timezone
        from datetime import timedelta
        
        return MultiSigTransaction.objects.create(
            transaction=transaction,
            required_signatures=required_signatures,
            expires_at=timezone.now() + timedelta(hours=expires_in_hours)
        )
    
    def sign_transaction(self, multi_sig_tx, signer_wallet):
        """
        Add a signature to a multi-signature transaction
        """
        # Verify signer hasn't already signed
        if TransactionSignature.objects.filter(
            multi_sig_transaction=multi_sig_tx,
            signer=signer_wallet
        ).exists():
            raise ValueError("Wallet has already signed this transaction")
        
        # Create signature
        message = f"{multi_sig_tx.transaction.tx_hash}:{signer_wallet.address}"
        signature = self.web3_client.w3.eth.account.sign_message(
            encode_defunct(text=message),
            private_key=self.web3_client.fernet.decrypt(
                signer_wallet.encrypted_private_key.encode()
            ).decode()
        )
        
        # Save signature
        TransactionSignature.objects.create(
            multi_sig_transaction=multi_sig_tx,
            signer=signer_wallet,
            signature=signature.signature.hex()
        )
        
        # Update signature count
        multi_sig_tx.current_signatures = TransactionSignature.objects.filter(
            multi_sig_transaction=multi_sig_tx
        ).count()
        multi_sig_tx.save()
        
        return multi_sig_tx.current_signatures >= multi_sig_tx.required_signatures