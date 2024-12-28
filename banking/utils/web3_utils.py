from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from django.conf import settings
import json
from cryptography.fernet import Fernet
from ..models import Wallet, Transaction

class Web3Client:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
        self.encryption_key = settings.ENCRYPTION_KEY
        self.fernet = Fernet(self.encryption_key)
    
    def create_wallet(self, user):
        account = Account.create()
        encrypted_private_key = self.fernet.encrypt(account.key.hex().encode())
        
        wallet = Wallet.objects.create(
            user=user,
            address=account.address,
            encrypted_private_key=encrypted_private_key.decode(),
            is_primary=not Wallet.objects.filter(user=user).exists()
        )
        return wallet
    
    def get_balance(self, wallet_address):
        balance_wei = self.w3.eth.get_balance(wallet_address)
        return Web3.from_wei(balance_wei, 'ether')
    
    def send_transaction(self, from_wallet, to_address, amount_ether):
        # Decrypt private key
        private_key = self.fernet.decrypt(from_wallet.encrypted_private_key.encode()).decode()
        
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(from_wallet.address)
        gas_price = self.w3.eth.gas_price
        
        transaction = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 21000,  # Standard ETH transfer
            'to': to_address,
            'value': Web3.to_wei(amount_ether, 'ether'),
            'data': b'',
            'chainId': self.w3.eth.chain_id
        }
        
        # Sign transaction
        signed = self.w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        # Create transaction record
        tx = Transaction.objects.create(
            from_wallet=from_wallet,
            to_address=to_address,
            amount=amount_ether,
            gas_price=Web3.from_wei(gas_price, 'gwei'),
            tx_hash=tx_hash.hex(),
            nonce=nonce
        )
        
        return tx