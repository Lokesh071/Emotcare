#!/bin/bash

# Set default port if PORT environment variable is not set
if [ -z "$PORT" ]; then
    export PORT=8080
    echo "PORT not set, using default: $PORT"
else
    echo "Using PORT from environment: $PORT"
fi

# Start the application with gunicorn
echo "Starting gunicorn on 0.0.0.0:$PORT"
exec gunicorn --bind 0.0.0.0:$PORT app:app --workers 2 --timeout 120
