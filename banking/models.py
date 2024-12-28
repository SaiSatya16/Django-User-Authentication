from django.db import models
from django.conf import settings
from eth_account.account import Account
import secrets

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=42, unique=True)
    encrypted_private_key = models.TextField()
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_primary']),
        ]

class Transaction(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    from_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='sent_transactions')
    to_address = models.CharField(max_length=42)
    amount = models.DecimalField(max_digits=24, decimal_places=18)
    gas_price = models.DecimalField(max_digits=24, decimal_places=18)
    gas_used = models.DecimalField(max_digits=24, decimal_places=18, null=True)
    tx_hash = models.CharField(max_length=66, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nonce = models.IntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['from_wallet', 'status']),
            models.Index(fields=['tx_hash']),
        ]

class MultiSigTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    required_signatures = models.IntegerField(default=2)
    current_signatures = models.IntegerField(default=0)
    signers = models.ManyToManyField(Wallet, through='TransactionSignature')
    expires_at = models.DateTimeField()

class TransactionSignature(models.Model):
    multi_sig_transaction = models.ForeignKey(MultiSigTransaction, on_delete=models.CASCADE)
    signer = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    signature = models.TextField()
    signed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['multi_sig_transaction', 'signer']