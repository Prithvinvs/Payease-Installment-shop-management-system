# Use offical Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt /app/

# Install python packages
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn

# Copy project files
COPY . /app/

# Create uploads, invoices, and backups directories
RUN mkdir -p uploads invoices backups instance

# Expose port
EXPOSE 5000

# Execute server run command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
