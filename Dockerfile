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

# Copy the requirements.txt file to the container to install Python dependencies
COPY requirements.txt ./

# Install the Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Before copying the application code, create the logs and qr_codes directories
# and ensure they are owned by the non-root user
RUN mkdir logs qr_codes && chown myuser:myuser logs qr_codes

# Copy the rest of the application's source code into the container
COPY --chown=myuser:myuser . .

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Switch to the 'myuser' user to run the application
USER myuser

# Run Flask application using the new entry point
CMD ["python", "run.py"]
