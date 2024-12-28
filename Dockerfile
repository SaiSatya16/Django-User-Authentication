# Dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create directories for static files
RUN mkdir -p /app/static /app/staticfiles /app/data

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt || \
    (pip install --no-cache-dir pysha3 && pip install --no-cache-dir -r requirements.txt)

# Copy project
COPY . /app/

# Create a non-root user
RUN useradd -m myuser
RUN chown -R myuser:myuser /app /app/static /app/staticfiles /app/data
USER myuser

# Run the application
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]