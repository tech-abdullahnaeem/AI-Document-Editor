FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    texlive-full \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    imagemagick \
    ghostscript \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads and downloads
RUN mkdir -p /app/fastapi_backend/uploads \
    && mkdir -p /app/fastapi_backend/downloads \
    && mkdir -p /app/fastapi_backend/temp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "fastapi_backend.main:app"]
