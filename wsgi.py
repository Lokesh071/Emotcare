#!/usr/bin/env python3
"""
WSGI entry point for EmotiCare application.
This file is used for deployment on platforms like Render, Heroku, etc.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# Create the Flask application instance
app = create_app()

# For debugging
print("✅ WSGI app created successfully")
print(f"✅ App instance: {app}")
print(f"✅ App name: {app.name}")

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting app on port {port}")
    # Run the application
    app.run(debug=False, host='0.0.0.0', port=port)