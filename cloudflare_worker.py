from flask.cli import load_dotenv
from app import create_app
import os

# Load environment variables
load_dotenv()

# Create the Flask app
app = create_app()

# Main function for Cloudflare Workers
def main(request):
    return app(request)
