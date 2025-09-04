"""
Crusont API - Vercel-Compatible FastAPI Application
A simple AI reverse proxy API designed for Vercel deployment
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crusont API",
    description="Free and Open AI API Gateway",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for demo purposes
# In production, you'd use a proper database
api_keys = {
    "demo-key-123": {
        "name": "Demo Key",
        "created_at": "2024-01-01",
        "usage": 0
    }
}

# Available models
AVAILABLE_MODELS = {
    "gpt-3.5-turbo": {
        "id": "gpt-3.5-turbo",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai"
    },
    "gpt-4": {
        "id": "gpt-4",
        "object": "model", 
        "created": 1687882411,
        "owned_by": "openai"
    },
    "gpt-4-turbo": {
        "id": "gpt-4-turbo",
        "object": "model",
        "created": 1698962400,
        "owned_by": "openai"
    }
}

def get_api_key(request: Request) -> Optional[str]:
    """Extract API key from request headers"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    return api_key in api_keys

async def proxy_to_openai(endpoint: str, data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Proxy request to OpenAI API"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.openai.com/v1/{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            result = await response.json()
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=result)
            return result

# Root endpoint - serve frontend
@app.get("/")
async def root():
    """Serve the main frontend page"""
    try:
        # Read the frontend index.html file
        frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
        with open(frontend_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="text/html",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except FileNotFoundError:
        return Response(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Crusont API</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 40px; }
                    .api-info { background: #f5f5f5; padding: 20px; border-radius: 8px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Crusont API</h1>
                        <p>Free and Open AI API Gateway</p>
                    </div>
                    <div class="api-info">
                        <h2>API Endpoints</h2>
                        <ul>
                            <li><strong>GET /v1/models</strong> - List available models</li>
                            <li><strong>POST /v1/chat/completions</strong> - Chat completions</li>
                            <li><strong>GET /health</strong> - Health check</li>
                        </ul>
                        <h3>Authentication</h3>
                        <p>Use API key in Authorization header: <code>Bearer your-api-key</code></p>
                        <p>Demo key: <code>demo-key-123</code></p>
                    </div>
                </div>
            </body>
            </html>
            """,
            media_type="text/html"
        )

# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Crusont API is running"}

# Models endpoint
@app.get("/v1/models")
async def get_models(request: Request):
    """List available models"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return {
        "object": "list",
        "data": list(AVAILABLE_MODELS.values())
    }

# Chat completions endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """Chat completions endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        data = await request.json()
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Proxy to OpenAI
        result = await proxy_to_openai("chat/completions", data, api_key)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error in chat completions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# API key management endpoints
@app.post("/api/keys")
async def create_api_key(request: Request):
    """Create a new API key"""
    try:
        data = await request.json()
        key_name = data.get("name", "New Key")
        
        # Generate a simple API key (in production, use proper key generation)
        import uuid
        new_key = f"key-{str(uuid.uuid4())[:8]}"
        
        api_keys[new_key] = {
            "name": key_name,
            "created_at": "2024-01-01",  # In production, use actual timestamp
            "usage": 0
        }
        
        return {"api_key": new_key, "message": "API key created successfully"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

@app.get("/api/keys")
async def list_api_keys():
    """List all API keys (for demo purposes)"""
    return {"api_keys": list(api_keys.keys())}

# Static file serving
@app.get("/styles.css")
async def serve_styles():
    """Serve CSS file"""
    try:
        css_path = os.path.join(os.path.dirname(__file__), "frontend", "styles.css")
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="text/css",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except FileNotFoundError:
        return Response(
            content="/* CSS not found */",
            media_type="text/css"
        )

@app.get("/script.js")
async def serve_script():
    """Serve JavaScript file"""
    try:
        js_path = os.path.join(os.path.dirname(__file__), "frontend", "script.js")
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except FileNotFoundError:
        return Response(
            content="// JS not found",
            media_type="application/javascript"
        )

@app.get("/favicon.ico")
async def serve_favicon():
    """Serve favicon"""
    try:
        favicon_path = os.path.join(os.path.dirname(__file__), "frontend", "favicon.ico")
        with open(favicon_path, 'rb') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="image/x-icon",
            headers={"Cache-Control": "public, max-age=31536000"}
        )
    except FileNotFoundError:
        # Return a simple 1x1 transparent PNG
        import base64
        png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
        return Response(
            content=png_data,
            media_type="image/x-icon"
        )

# Catch-all for any other routes
@app.get("/{path:path}")
async def catch_all(path: str):
    """Catch-all route for debugging"""
    return JSONResponse(
        content={
            "error": "Not found",
            "path": path,
            "message": "This endpoint doesn't exist",
            "available_endpoints": [
                "/",
                "/health", 
                "/v1/models",
                "/v1/chat/completions",
                "/api/keys"
            ]
        },
        status_code=404
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
