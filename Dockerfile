# Base image with Python
FROM python:3.10-slim

# Install system dependencies (poppler, tesseract, fonts)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-khm \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the Render expected port
EXPOSE 10000

# Run with Gunicorn, binding to $PORT
CMD gunicorn -b 0.0.0.0:$PORT --timeout 120 app:app


