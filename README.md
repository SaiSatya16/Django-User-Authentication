# Django Authentication System

A comprehensive Django-based authentication system that provides user registration, login, password management, and profile features. Built with modern best practices and Docker support.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Traditional Setup](#traditional-setup)
  - [Docker Setup](#docker-setup)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Available URLs](#available-urls)
- [Features in Detail](#features-in-detail)
- [Docker Deployment](#docker-deployment)
- [Development Guidelines](#development-guidelines)
- [Production Deployment](#production-deployment)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- User Registration with email verification
- Login with username or email
- Password Reset functionality
- Password Change for logged-in users
- User Profile management
- Custom User Model with additional fields
- Bootstrap-based responsive UI
- Dashboard for authenticated users
- Docker support for easy deployment
- SQLite database for simplicity

## Prerequisites

### Traditional Setup
- Python 3.12+
- Django 5.1+
- Virtual Environment (recommended)

### Docker Setup
- Docker
- Docker Compose

## Installation

### Traditional Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/django_auth_project.git
cd django_auth_project
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install django
```

4. Apply migrations:
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

### Docker Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/django_auth_project.git
cd django_auth_project
```

2. Create required directories:
```bash
mkdir data
```

3. Build and start the containers:
```bash
docker-compose up -d --build
```

4. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Project Structure

```bash
django_auth_project/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── docker-compose.prod.yml
    ├── requirements.txt
    ├── .dockerignore
    ├── manage.py
    ├── data/
    │   └── db.sqlite3
    ├── auth_project/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── accounts/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── urls.py
    │   ├── views.py
    │   └── templates/
    │       └── accounts/
    │           ├── login.html
    │           ├── signup.html
    │           ├── forgot_password.html
    │           ├── change_password.html
    │           ├── dashboard.html
    │           └── profile.html
    ├── static/
    │   └── css/
    │       └── style.css
    ├── templates/
    │   └── base.html
    └── nginx/                 # Production only
        ├── Dockerfile
        └── nginx.conf
```

## Configuration

### Key Settings (settings.py)

```bash
# Auth Settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data', 'db.sqlite3'),
    }
}
```

## Available URLs

- `/accounts/` - Login page (default)
- `/accounts/signup/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/forgot-password/` - Password reset
- `/accounts/change-password/` - Password change
- `/accounts/dashboard/` - User dashboard
- `/accounts/profile/` - User profile
- `/admin/` - Admin interface

## Features in Detail

### Custom User Model
- Extends Django's AbstractUser
- Email field is unique and required
- Tracks last update time
- Compatible with Django's authentication system

### Forms
- `SignUpForm`: User registration with email validation
- `CustomAuthenticationForm`: Login with username or email
- Built-in Django forms for password management

### Templates
- Bootstrap 5.1.3 based
- Responsive design
- Clean and modern UI
- Flash messages for user feedback

## Docker Deployment

### Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Run Django commands
docker-compose exec web python manage.py [command]

# Stop services
docker-compose down
```

### Production

1. Update environment variables in docker-compose.prod.yml
2. Build and run:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Database Management

```bash
# Backup
docker-compose exec web sqlite3 data/db.sqlite3 ".backup '/app/data/backup.sqlite3'"

# Copy to host
docker cp $(docker-compose ps -q web):/app/data/backup.sqlite3 ./data/
```

## Development Guidelines

1. Code Style
   - Follow PEP 8 guidelines
   - Use meaningful variable and function names
   - Add comments for complex logic

2. Testing
   - Write unit tests for new features
   - Test all forms and views
   - Ensure proper error handling

3. Git Workflow
   - Create feature branches
   - Write descriptive commit messages
   - Keep commits atomic and focused

## Production Deployment

1. Security Settings
```bash
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-secure-key'
```

2. SSL/HTTPS Configuration
   - Configure SSL certificate
   - Force HTTPS
   - Set secure cookie settings

3. Static Files
   - Run collectstatic
   - Configure static file serving
   - Set up media files handling

## Security Considerations

1. General Security
   - Keep Django updated
   - Use strong passwords
   - Enable CSRF protection
   - Set secure cookie flags

2. Docker Security
   - Use official base images
   - Don't run as root
   - Regularly update images
   - Secure environment variables

3. Database Security
   - Regular backups
   - Proper file permissions
   - Secure database credentials

## Troubleshooting

### Common Issues

1. Migration Issues
```bash
# Reset migrations
rm -r accounts/migrations
python manage.py makemigrations accounts
python manage.py migrate
```

2. Static Files
```bash
# Collect static files
python manage.py collectstatic --no-input
```

3. Docker Issues
```bash
# Permission issues
docker-compose exec web mkdir -p /app/data

# Port conflicts
lsof -i :8000
```

For more information or support, please open an issue on the GitHub repository.