#!/bin/bash

# Set default port if PORT environment variable is not set
if [ -z "$PORT" ]; then
    export PORT=8080
    echo "PORT not set, using default: $PORT"
else
    echo "Using PORT from environment: $PORT"
fi

# Optimize TensorFlow for memory usage
export TF_CPP_MIN_LOG_LEVEL=2
export TF_ENABLE_ONEDNN_OPTS=0
export OMP_NUM_THREADS=1

# Start the application with gunicorn (single worker for memory efficiency)
echo "Starting gunicorn on 0.0.0.0:$PORT"
exec gunicorn --bind 0.0.0.0:$PORT app:app --workers 1 --timeout 300 --max-requests 1000 --max-requests-jitter 100
