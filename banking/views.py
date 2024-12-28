from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Transaction, MultiSigTransaction, Wallet, TransactionSignature
from .utils.web3_utils import Web3Client
from .utils.zkp_utils import BalanceProof
from .utils.multisig_utils import MultiSigManager
from .forms import TransactionForm
from django.db.models import Q

from decimal import Decimal
import requests

def get_eth_price():
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
        data = response.json()
        return Decimal(str(data['ethereum']['usd']))
    except:
        return None

@login_required
def wallet_dashboard(request):
    try:
        web3_client = Web3Client()
        wallets = Wallet.objects.filter(user=request.user)
        
        # Initialize wallet if user has none
        if not wallets.exists():
            try:
                wallet = web3_client.create_wallet(request.user)
                messages.success(request, f"Created new wallet: {wallet.address}")
                wallets = Wallet.objects.filter(user=request.user)
            except Exception as e:
                messages.error(request, f"Error creating wallet: {str(e)}")
                return render(request, 'banking/dashboard.html', {'error': str(e)})
        
        # Get ETH price
        eth_price = get_eth_price()
        
        # Get wallet balances
        wallet_balances = []
        for wallet in wallets:
            try:
                balance = web3_client.get_balance(wallet.address)
                wallet_info = {
                    'wallet': wallet,
                    'balance': balance,
                    'balance_formatted': f"{balance:.4f}"
                }
                if eth_price:
                    wallet_info['fiat_value'] = balance * eth_price
                wallet_balances.append(wallet_info)
            except Exception as e:
                messages.warning(request, f"Could not fetch balance for wallet {wallet.address}: {str(e)}")
                wallet_balances.append({
                    'wallet': wallet,
                    'balance': 0,
                    'balance_formatted': "0.0000",
                    'error': str(e)
                })
        
        # Get recent transactions
        recent_transactions = Transaction.objects.filter(
            Q(from_wallet__in=wallets) | 
            Q(to_address__in=[w.address for w in wallets])
        ).order_by('-created_at')[:5]
        
        context = {
            'wallet_balances': wallet_balances,
            'recent_transactions': recent_transactions,
            'eth_price': eth_price
        }
        
        return render(request, 'banking/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, 'banking/dashboard.html', {'error': str(e)})

@login_required
def create_wallet(request):
    if request.method == 'POST':
        web3_client = Web3Client()
        wallet = web3_client.create_wallet(request.user)
        messages.success(request, f"New wallet created: {wallet.address}")
    return redirect('wallet_dashboard')

@login_required
def send_transaction(request):
    try:
        if request.method == 'POST':
            form = TransactionForm(request.POST)
            if form.is_valid():
                web3_client = Web3Client()
                from_wallet = get_object_or_404(
                    Wallet,
                    user=request.user,
                    address=request.POST.get('from_wallet')
                )
                
                # Check wallet balance
                balance = web3_client.get_balance(from_wallet.address)
                if balance < form.cleaned_data['amount']:
                    messages.error(request, "Insufficient balance")
                    return redirect('banking:send_transaction')
                
                try:
                    tx = web3_client.send_transaction(
                        from_wallet,
                        form.cleaned_data['to_address'],
                        form.cleaned_data['amount']
                    )
                    messages.success(request, f"Transaction sent: {tx.tx_hash}")
                    return redirect('banking:transaction_detail', tx_hash=tx.tx_hash)
                except Exception as e:
                    messages.error(request, f"Transaction failed: {str(e)}")
        else:
            form = TransactionForm()
        
        wallets = Wallet.objects.filter(user=request.user)
        
        # Get wallet balances
        wallet_balances = []
        web3_client = Web3Client()
        for wallet in wallets:
            try:
                balance = web3_client.get_balance(wallet.address)
                wallet_balances.append({
                    'address': wallet.address,
                    'balance': f"{balance:.6f}"
                })
            except Exception as e:
                wallet_balances.append({
                    'address': wallet.address,
                    'balance': "Error fetching balance"
                })
        
        context = {
            'form': form,
            'wallets': wallet_balances
        }
        return render(request, 'banking/send_transaction.html', context)
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('banking:wallet_dashboard')

@login_required
def transaction_history(request):
    wallets = Wallet.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(
        Q(from_wallet__in=wallets) | Q(to_address__in=[w.address for w in wallets])
    ).order_by('-created_at')
    
    context = {
        'transactions': transactions
    }
    return render(request, 'banking/transaction_history.html', context)

@login_required
def create_multisig_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                web3_client = Web3Client()
                multisig_manager = MultiSigManager(web3_client)
                
                from_wallet = Wallet.objects.get(
                    user=request.user,
                    address=request.POST.get('from_wallet')
                )
                
                tx = web3_client.send_transaction(
                    from_wallet,
                    form.cleaned_data['to_address'],
                    form.cleaned_data['amount']
                )
                
                required_signatures = int(request.POST.get('required_signatures', 2))
                multi_sig_tx = multisig_manager.create_multisig_transaction(
                    tx, required_signatures
                )
                
                messages.success(request, "Multi-signature transaction created")
                return redirect('banking:multisig_detail', tx_hash=tx.tx_hash)
            except Exception as e:
                messages.error(request, f"Error creating transaction: {str(e)}")
    else:
        form = TransactionForm()
    
    wallets = Wallet.objects.filter(user=request.user)
    context = {
        'form': form,
        'wallets': wallets
    }
    return render(request, 'banking/create_multisig.html', context)

@login_required
def transaction_detail(request, tx_hash):
    """
    Display detailed information about a specific transaction
    """
    # Get user's wallets
    user_wallets = Wallet.objects.filter(user=request.user)
    user_addresses = [w.address for w in user_wallets]
    
    # Get transaction
    transaction = get_object_or_404(
        Transaction,
        tx_hash=tx_hash,
        from_wallet__in=user_wallets
    )
    
    # Check if this is a multisig transaction
    try:
        multisig = transaction.multisigtransaction
        return redirect('multisig_detail', tx_hash=tx_hash)
    except MultiSigTransaction.DoesNotExist:
        multisig = None
    
    # Get transaction receipt from blockchain
    web3_client = Web3Client()
    try:
        receipt = web3_client.w3.eth.get_transaction_receipt(tx_hash)
        block_info = web3_client.w3.eth.get_block(receipt['blockNumber'])
        
        context = {
            'transaction': transaction,
            'receipt': {
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'status': 'Success' if receipt['status'] == 1 else 'Failed',
                'timestamp': block_info['timestamp'],
                'confirmations': web3_client.w3.eth.block_number - receipt['blockNumber']
            }
        }
    except Exception as e:
        context = {
            'transaction': transaction,
            'error': str(e)
        }
    
    return render(request, 'banking/transaction_detail.html', context)

@login_required
def multisig_detail(request, tx_hash):
    """
    Display details of a multi-signature transaction
    """
    # Get user's wallets
    user_wallets = Wallet.objects.filter(user=request.user)
    
    # Get transaction and multisig details
    transaction = get_object_or_404(Transaction, tx_hash=tx_hash)
    multisig = get_object_or_404(MultiSigTransaction, transaction=transaction)
    
    # Check if user can sign this transaction
    can_sign = (
        user_wallets.exists() and
        not TransactionSignature.objects.filter(
            multi_sig_transaction=multisig,
            signer__in=user_wallets
        ).exists() and
        multisig.current_signatures < multisig.required_signatures and
        multisig.expires_at > timezone.now()
    )
    
    context = {
        'multisig': multisig,
        'can_sign': can_sign,
        'signatures': TransactionSignature.objects.filter(
            multi_sig_transaction=multisig
        ).select_related('signer').order_by('signed_at')
    }
    
    return render(request, 'banking/multisig_detail.html', context)

@login_required
def sign_multisig(request, tx_hash):
    """
    Sign a multi-signature transaction
    """
    if request.method != 'POST':
        return redirect('multisig_detail', tx_hash=tx_hash)
    
    # Get transaction and multisig details
    transaction = get_object_or_404(Transaction, tx_hash=tx_hash)
    multisig = get_object_or_404(MultiSigTransaction, transaction=transaction)
    
    # Get user's primary wallet
    try:
        signer_wallet = Wallet.objects.get(
            user=request.user,
            is_primary=True
        )
    except Wallet.DoesNotExist:
        messages.error(request, "No primary wallet found")
        return redirect('multisig_detail', tx_hash=tx_hash)
    
    # Check if transaction can be signed
    if multisig.current_signatures >= multisig.required_signatures:
        messages.error(request, "Transaction already has required signatures")
        return redirect('multisig_detail', tx_hash=tx_hash)
    
    if multisig.expires_at <= timezone.now():
        messages.error(request, "Transaction has expired")
        return redirect('multisig_detail', tx_hash=tx_hash)
    
    # Check if user already signed
    if TransactionSignature.objects.filter(
        multi_sig_transaction=multisig,
        signer=signer_wallet
    ).exists():
        messages.error(request, "You have already signed this transaction")
        return redirect('multisig_detail', tx_hash=tx_hash)
    
    try:
        # Initialize Web3 client and MultiSig manager
        web3_client = Web3Client()
        multisig_manager = MultiSigManager(web3_client)
        
        # Add signature
        is_complete = multisig_manager.sign_transaction(multisig, signer_wallet)
        
        if is_complete:
            messages.success(
                request,
                "Transaction signed and executed successfully!"
            )
        else:
            messages.success(
                request,
                "Transaction signed successfully. Awaiting more signatures."
            )
            
    except Exception as e:
        messages.error(request, f"Error signing transaction: {str(e)}")
    
    return redirect('multisig_detail', tx_hash=tx_hash)

@login_required
def generate_balance_proof(request):
    """
    Generate a zero-knowledge proof of sufficient balance
    """
    if request.method != 'POST':
        return render(request, 'banking/balance_proof.html')
    
    try:
        # Get user's primary wallet
        wallet = get_object_or_404(
            Wallet,
            user=request.user,
            is_primary=True
        )
        
        # Get current balance
        web3_client = Web3Client()
        balance = web3_client.get_balance(wallet.address)
        
        # Get threshold from form
        threshold = float(request.POST.get('threshold', 0))
        
        # Generate proof
        proof_generator = BalanceProof()
        proof = proof_generator.generate_proof(
            balance=float(balance),
            threshold=threshold
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'proof': proof
            })
        
        messages.success(request, "Balance proof generated successfully")
        return render(request, 'banking/balance_proof.html', {
            'proof': proof,
            'threshold': threshold
        })
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        
        messages.error(request, f"Error generating proof: {str(e)}")
        return render(request, 'banking/balance_proof.html')