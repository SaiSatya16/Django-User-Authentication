# banking/tasks.py
from django.conf import settings
from .models import Transaction
from .utils.web3_utils import Web3Client
import time

def monitor_transactions():
    web3_client = Web3Client()
    
    while True:
        pending_txs = Transaction.objects.filter(status=Transaction.PENDING)
        
        for tx in pending_txs:
            try:
                receipt = web3_client.w3.eth.get_transaction_receipt(tx.tx_hash)
                if receipt:
                    tx.status = (
                        Transaction.COMPLETED 
                        if receipt['status'] == 1 
                        else Transaction.FAILED
                    )
                    tx.gas_used = receipt['gasUsed']
                    tx.save()
            except Exception as e:
                print(f"Error monitoring transaction {tx.tx_hash}: {str(e)}")
        
        time.sleep(15)  # Wait 15 seconds between checks