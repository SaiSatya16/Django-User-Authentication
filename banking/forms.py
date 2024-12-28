from django import forms
from web3 import Web3
from decimal import Decimal

class TransactionForm(forms.Form):
    to_address = forms.CharField(
        max_length=42,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0x...',
            'pattern': '^0x[a-fA-F0-9]{40}$'
        })
    )
    amount = forms.DecimalField(
        max_digits=24,
        decimal_places=18,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.000000000000000001',
            'min': '0.000000000000000001'
        })
    )
    
    def clean_to_address(self):
        address = self.cleaned_data['to_address']
        if not Web3.is_address(address):
            raise forms.ValidationError("Invalid Ethereum address")
        return Web3.to_checksum_address(address)
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= Decimal('0'):
            raise forms.ValidationError("Amount must be greater than 0")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        # Add any cross-field validation here if needed
        return cleaned_data