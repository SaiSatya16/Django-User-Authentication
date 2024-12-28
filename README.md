# Secure Banking - Ethereum Wallet Management System

A comprehensive Django-based web application for secure Ethereum wallet management, featuring multi-signature transactions and zero-knowledge proofs. This enterprise-grade solution provides robust security features while maintaining user-friendly interfaces for cryptocurrency management.

## Table of Contents

1. [Features](#features)
2. [Technical Architecture](#technical-architecture)
3. [Security Architecture](#security-architecture)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Development Setup](#development-setup)
8. [Production Deployment](#production-deployment)
9. [API Documentation](#api-documentation)
10. [Testing](#testing)
11. [Security Considerations](#security-considerations)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)
14. [License](#license)

## Features

### Core Features
- User Authentication & Authorization
  - Email-based registration
  - Two-factor authentication support
  - Role-based access control
  - Password recovery system
  - Session management

- Wallet Management
  - Multiple wallet support per user
  - Encrypted private key storage
  - Real-time balance tracking
  - ETH/USD price conversion
  - Transaction history

- Transaction Operations
  - ETH transfers
  - Gas price optimization
  - Transaction status monitoring
  - Receipt verification
  - Nonce management

### Advanced Features
- Multi-Signature Transactions
  - Configurable signature thresholds
  - Time-bound approval windows
  - Signature verification
  - Transaction lifecycle management

- Zero-Knowledge Proofs
  - Balance verification without disclosure
  - Range proofs for threshold checking
  - Cryptographic commitment schemes
  - Privacy-preserving verification

## Technical Architecture

### System Components
```
secure-banking/
├── accounts/                 # User authentication
│   ├── models.py            # CustomUser model
│   ├── forms.py             # Authentication forms
│   └── views.py             # Auth views
├── banking/                 # Core banking logic
│   ├── models.py            # Transaction models
│   ├── utils/               # Utility functions
│   │   ├── web3_utils.py    # Web3 integration
│   │   ├── zkp_utils.py     # ZK proofs
│   │   └── multisig_utils.py# Multi-sig logic
│   └── views.py             # Banking views
├── templates/               # HTML templates
├── static/                 # Static assets
└── auth_project/           # Project settings
```

### Database Schema

#### Users & Authentication
```sql
CustomUser:
- id: BigAutoField (PK)
- email: EmailField (unique)
- username: CharField
- password: CharField (hashed)
- last_updated: DateTimeField

Wallet:
- id: BigAutoField (PK)
- user: ForeignKey(CustomUser)
- address: CharField(42)
- encrypted_private_key: TextField
- is_primary: Boolean
- created_at: DateTimeField
```

#### Transactions
```sql
Transaction:
- id: BigAutoField (PK)
- from_wallet: ForeignKey(Wallet)
- to_address: CharField(42)
- amount: DecimalField(24,18)
- gas_price: DecimalField
- status: CharField
- tx_hash: CharField(66)
- nonce: Integer
- created_at: DateTimeField

MultiSigTransaction:
- transaction: OneToOneField(Transaction)
- required_signatures: Integer
- current_signatures: Integer
- expires_at: DateTimeField

TransactionSignature:
- multi_sig_transaction: ForeignKey(MultiSigTransaction)
- signer: ForeignKey(Wallet)
- signature: TextField
- signed_at: DateTimeField
```

## Security Architecture

### Key Security Features

1. Private Key Management
```python
# Encryption at rest using Fernet
encryption_key = settings.ENCRYPTION_KEY
fernet = Fernet(encryption_key)
encrypted_private_key = fernet.encrypt(private_key.encode())
```

2. Multi-Signature Implementation
```python
# Signature verification
def verify_signature(self, signature, message, address):
    recovered_address = web3.eth.account.recover_message(
        encode_defunct(text=message),
        signature=signature
    )
    return recovered_address.lower() == address.lower()
```

3. Zero-Knowledge Proofs
```python
# Balance proof generation
def generate_proof(balance, threshold):
    commitment = multiply(G1, balance)
    difference = balance - threshold
    proof = create_range_proof(difference, range_max)
    return proof
```

### Security Measures
- CSRF protection enabled
- SQL injection prevention
- XSS protection
- Rate limiting
- Input validation
- Secure headers
- Session security
- Encrypted storage

## Prerequisites

### System Requirements
- Python 3.12+
- Node.js 14+
- Docker 20.10+
- 2GB RAM minimum
- 20GB storage

### Dependencies
```
Django==5.1.2
web3==6.11.3
py-ecc==7.0.0
cryptography==41.0.7
gunicorn==21.2.0
```

### External Services
- Ethereum Node (Infura/Geth)
- SMTP Server
- Redis (optional caching)

## Installation

### Local Setup

1. Clone and setup virtual environment:
```bash
git clone <repository-url>
cd secure-banking
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

3. Environment configuration:
```bash
cp .env.example .env

# Required variables
DJANGO_SECRET_KEY=<secure-random-key>
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/<your-project-id>
ENCRYPTION_KEY=<fernet-encryption-key>
DEBUG=0
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Docker Setup

1. Development environment:
```bash
# Build images
docker-compose build

# Run services
docker-compose up -d

# Create database
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

2. Production environment:
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy services
docker-compose -f docker-compose.prod.yml up -d

# Configure Nginx
docker-compose exec nginx nginx -t
docker-compose exec nginx nginx -s reload
```

## Configuration

### Django Settings

Key settings in `settings.py`:
```python
# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Web3 settings
WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

# Authentication settings
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'banking:wallet_dashboard'
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /app/staticfiles/;
    }
}
```

## Development Setup

### Local Development

1. Setup pre-commit hooks:
```bash
pre-commit install
```

2. Run tests:
```bash
python manage.py test
pytest
coverage run manage.py test
```

3. Code quality checks:
```bash
flake8
black .
isort .
```

### Development Tools
- Django Debug Toolbar
- Coverage.py for test coverage
- Black for code formatting
- Flake8 for linting
- pytest for testing

## Production Deployment

### Deployment Checklist

1. Security configuration:
```bash
# Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"
```

2. SSL/TLS setup:
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d example.com
```

3. Database backup:
```bash
# Backup
docker-compose exec web python manage.py dumpdata > backup.json

# Restore
docker-compose exec web python manage.py loaddata backup.json
```

### Monitoring

1. Setup logging:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

2. Health checks:
```python
HEALTHCHECK_URLS = {
    'db': 'django.contrib.db.backends.base.DatabaseWrapper',
    'cache': 'django.core.cache.backends.base.BaseCache',
}
```

## API Documentation

### Authentication Endpoints

```
POST /accounts/login/
- username/email
- password
Returns: JWT token

POST /accounts/signup/
- username
- email
- password1
- password2
Returns: User object

POST /accounts/logout/
- Authorization header
Returns: Success message
```

### Banking Endpoints

```
GET /banking/dashboard/
Returns: Wallet balances, recent transactions

POST /banking/create-wallet/
Returns: New wallet address

POST /banking/send-transaction/
- from_wallet
- to_address
- amount
Returns: Transaction hash

GET /banking/transactions/
Returns: Transaction history

POST /banking/multisig/create/
- from_wallet
- to_address
- amount
- required_signatures
Returns: MultiSig transaction object
```

## Testing

### Unit Tests

```python
# Test wallet creation
def test_create_wallet(self):
    user = CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    web3_client = Web3Client()
    wallet = web3_client.create_wallet(user)
    self.assertTrue(Web3.is_address(wallet.address))
    self.assertTrue(wallet.encrypted_private_key)
```

### Integration Tests

```python
# Test transaction flow
def test_transaction_flow(self):
    self.client.login(username='testuser', password='testpass123')
    response = self.client.post('/banking/send-transaction/', {
        'from_wallet': self.wallet.address,
        'to_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
        'amount': '0.1'
    })
    self.assertEqual(response.status_code, 302)
    tx = Transaction.objects.latest('created_at')
    self.assertEqual(tx.status, Transaction.PENDING)
```

## Security Considerations

### Private Key Management
- Private keys are encrypted at rest using Fernet symmetric encryption
- Keys are never stored in plaintext
- Key material is stored in secure environment variables

### Transaction Security
- Nonce management prevents replay attacks
- Gas price validation prevents overspending
- Amount validation prevents overflow
- Address checksum validation

### Multi-Signature Security
- Time-bound signatures prevent replay attacks
- Signature count validation
- Signer uniqueness validation
- Transaction expiration

### Zero-Knowledge Proofs
- Range proof validation
- Commitment scheme security
- Proof verification
- Privacy preservation

## Troubleshooting

### Common Issues

1. Transaction Failures
```python
# Check gas price
web3_client = Web3Client()
gas_price = web3_client.w3.eth.gas_price
print(f"Current gas price: {gas_price} wei")

# Check nonce
nonce = web3_client.w3.eth.get_transaction_count(wallet.address)
print(f"Current nonce: {nonce}")
```

2. Multi-Signature Issues
```python
# Check signature status
multisig = MultiSigTransaction.objects.get(transaction__tx_hash=tx_hash)
signatures = TransactionSignature.objects.filter(multi_sig_transaction=multisig)
print(f"Signatures: {signatures.count()}/{multisig.required_signatures}")
```

### Debugging Tools

1. Web3 Connection
```python
# Test connection
def test_web3_connection():
    web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    return web3.is_connected()
```

2. Transaction Monitoring
```python
# Monitor transaction status
def get_transaction_status(tx_hash):
    try:
        receipt = web3.eth.get_transaction_receipt(tx_hash)
        return receipt['status']
    except Exception as e:
        return f"Error: {str(e)}"
```

## Contributing

### Development Process

1. Fork and clone:
```bash
git clone https://github.com/yourusername/secure-banking.git
cd secure-banking
```

2. Create branch:
```bash
git checkout -b feature/your-feature-name
```

3. Development workflow:
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Check code quality
flake8
black .
isort .

# Run pre-commit hooks
pre-commit run --all-files
```

## Acknowledgments

- Django Framework for web framework
- Web3.py for Ethereum integration
- py-ecc for zero-knowledge proofs
- Fernet for encryption
- Bootstrap for frontend
- Docker for containerization

For updates and support, visit the [project repository](https://github.com/yourusername/secure-banking).