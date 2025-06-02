FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for TensorFlow and OpenCV
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    libffi-dev \
    libssl-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy and make startup script executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Create necessary directories
RUN mkdir -p temp_sessions

# Expose port
EXPOSE 8080

# Use startup script
CMD ["/start.sh"]
