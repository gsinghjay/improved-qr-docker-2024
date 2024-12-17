# Dockerfile for QR Code Generator application
# 
# This Dockerfile creates a production-ready container for the QR code generator
# application. It uses Python 3.12 slim image as base and sets up a non-root
# user for security.
FROM python:3.12-slim-bullseye

# Set the working directory to /app in the container
WORKDIR /app

# Create a non-root user named 'myuser' with a home directory
RUN useradd -m myuser

# Install PostgreSQL client for database connection checking
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy and set permissions for entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy the requirements.txt file to the container to install Python dependencies
COPY requirements.txt ./

# Install the Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/qr_codes /app/migrations /app/migrations/versions && \
    chown -R myuser:myuser /app/logs /app/qr_codes /app/migrations && \
    chmod -R 755 /app/migrations

# Copy the rest of the application's source code into the container
COPY --chown=myuser:myuser . .

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Switch to the non-root user
USER myuser

# Set the entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
