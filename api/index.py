"""
Vercel entry point for the API
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main_single import app

# Export the FastAPI app for Vercel
handler = app
