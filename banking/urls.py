from django.urls import path
from . import views

app_name = 'banking'  # Add namespace

urlpatterns = [
    path('dashboard/', views.wallet_dashboard, name='wallet_dashboard'),
    path('create-wallet/', views.create_wallet, name='create_wallet'),
    path('send-transaction/', views.send_transaction, name='send_transaction'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transaction/<str:tx_hash>/', views.transaction_detail, name='transaction_detail'),
    path('multisig/create/', views.create_multisig_transaction, name='create_multisig'),
    path('multisig/<str:tx_hash>/', views.multisig_detail, name='multisig_detail'),
    path('multisig/<str:tx_hash>/sign/', views.sign_multisig, name='sign_multisig'),
    path('balance-proof/', views.generate_balance_proof, name='balance_proof'),
]