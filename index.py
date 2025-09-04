"""
Vercel entry point for Crusont API
"""

from api import app

# Export the FastAPI app for Vercel
handler = app
