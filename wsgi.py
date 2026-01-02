"""
WSGI entry point for production deployment
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

from app import app

if __name__ == "__main__":
    app.run()
