# Use official Python image (slim)
FROM python:3.10-slim

# install system packages (poppler, tesseract + khmer language files) and useful tools
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential \
      poppler-utils \
      tesseract-ocr \
      tesseract-ocr-khm \
      libgl1 \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# set workdir
WORKDIR /app

# copy python deps first (cache)
COPY requirements.txt .

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# ensure uploads and static exist
RUN mkdir -p uploads static

# env
ENV PYTHONUNBUFFERED=1
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin

# expose port
EXPOSE 5000

# run with gunicorn; app:app must match your Flask app variable
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers", "2", "--timeout", "120"]
