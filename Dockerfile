# Use Python 3.13 slim
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for Pillow, cryptography, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libfreetype6-dev \
    libffi-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir streamlit

# Copy project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit frontend
CMD ["python", "-m", "streamlit", "run", "streamlit_frontend_threading.py", "--server.port=8501", "--server.address=0.0.0.0"]
