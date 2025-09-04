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
    # Chat models
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
    },
    "gpt-4o": {
        "id": "gpt-4o",
        "object": "model",
        "created": 1715366400,
        "owned_by": "openai"
    },
    # Embedding models
    "text-embedding-ada-002": {
        "id": "text-embedding-ada-002",
        "object": "model",
        "created": 1671217299,
        "owned_by": "openai"
    },
    "text-embedding-3-small": {
        "id": "text-embedding-3-small",
        "object": "model",
        "created": 1705953181,
        "owned_by": "openai"
    },
    "text-embedding-3-large": {
        "id": "text-embedding-3-large",
        "object": "model",
        "created": 1705953181,
        "owned_by": "openai"
    },
    # Moderation models
    "text-moderation-latest": {
        "id": "text-moderation-latest",
        "object": "model",
        "created": 1687882411,
        "owned_by": "openai"
    },
    "text-moderation-stable": {
        "id": "text-moderation-stable",
        "object": "model",
        "created": 1687882411,
        "owned_by": "openai"
    },
    # Audio models
    "whisper-1": {
        "id": "whisper-1",
        "object": "model",
        "created": 1677532384,
        "owned_by": "openai"
    },
    # Image models
    "dall-e-2": {
        "id": "dall-e-2",
        "object": "model",
        "created": 1649880484,
        "owned_by": "openai"
    },
    "dall-e-3": {
        "id": "dall-e-3",
        "object": "model",
        "created": 1698785189,
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
        # Debug information
        logger.info(f"Root endpoint called - Current working directory: {os.getcwd()}")
        logger.info(f"API file location: {__file__}")
        logger.info(f"API file directory: {os.path.dirname(__file__)}")
        # Read the frontend index.html file
        # Try multiple possible paths for Vercel deployment
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "frontend", "index.html"),
            os.path.join(os.getcwd(), "frontend", "index.html"),
            "frontend/index.html",
            "index.html"
        ]
        
        frontend_path = None
        for path in possible_paths:
            if os.path.exists(path):
                frontend_path = path
                break
        
        if not frontend_path:
            raise FileNotFoundError("Frontend index.html not found")
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

# Simple test endpoint
@app.get("/test")
async def test():
    """Simple test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

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

# Embeddings endpoint
@app.post("/v1/embeddings")
async def embeddings(request: Request):
    """Embeddings endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        data = await request.json()
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Proxy to OpenAI
        result = await proxy_to_openai("embeddings", data, api_key)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error in embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Moderations endpoint
@app.post("/v1/moderations")
async def moderations(request: Request):
    """Moderations endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        data = await request.json()
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Proxy to OpenAI
        result = await proxy_to_openai("moderations", data, api_key)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error in moderations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Audio transcription endpoint
@app.post("/v1/audio/transcriptions")
async def audio_transcriptions(request: Request):
    """Audio transcription endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Handle multipart form data
        form = await request.form()
        file = form.get("file")
        model = form.get("model", "whisper-1")
        language = form.get("language")
        prompt = form.get("prompt")
        response_format = form.get("response_format", "json")
        temperature = form.get("temperature", "0")
        
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Prepare form data for OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        data = {
            "model": model,
            "response_format": response_format,
            "temperature": float(temperature)
        }
        if language:
            data["language"] = language
        if prompt:
            data["prompt"] = prompt
        
        # Read file content
        file_content = await file.read()
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field("file", file_content, filename=file.filename, content_type=file.content_type)
        for key, value in data.items():
            form_data.add_field(key, str(value))
        
        url = "https://api.openai.com/v1/audio/transcriptions"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data, headers=headers) as response:
                result = await response.json()
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=result)
                return result
        
    except Exception as e:
        logger.error(f"Error in audio transcription: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Audio translation endpoint
@app.post("/v1/audio/translations")
async def audio_translations(request: Request):
    """Audio translation endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Handle multipart form data
        form = await request.form()
        file = form.get("file")
        model = form.get("model", "whisper-1")
        prompt = form.get("prompt")
        response_format = form.get("response_format", "json")
        temperature = form.get("temperature", "0")
        
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Prepare form data for OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        data = {
            "model": model,
            "response_format": response_format,
            "temperature": float(temperature)
        }
        if prompt:
            data["prompt"] = prompt
        
        # Read file content
        file_content = await file.read()
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field("file", file_content, filename=file.filename, content_type=file.content_type)
        for key, value in data.items():
            form_data.add_field(key, str(value))
        
        url = "https://api.openai.com/v1/audio/translations"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data, headers=headers) as response:
                result = await response.json()
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=result)
                return result
        
    except Exception as e:
        logger.error(f"Error in audio translation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Image generation endpoint
@app.post("/v1/images/generations")
async def image_generations(request: Request):
    """Image generation endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        data = await request.json()
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Proxy to OpenAI
        result = await proxy_to_openai("images/generations", data, api_key)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error in image generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Image editing endpoint
@app.post("/v1/images/edits")
async def image_edits(request: Request):
    """Image editing endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Handle multipart form data
        form = await request.form()
        image = form.get("image")
        mask = form.get("mask")
        prompt = form.get("prompt")
        model = form.get("model", "dall-e-2")
        n = form.get("n", "1")
        size = form.get("size", "1024x1024")
        response_format = form.get("response_format", "url")
        user = form.get("user")
        
        if not image or not prompt:
            raise HTTPException(status_code=400, detail="Image and prompt are required")
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Prepare form data for OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field("image", await image.read(), filename=image.filename, content_type=image.content_type)
        form_data.add_field("prompt", prompt)
        form_data.add_field("model", model)
        form_data.add_field("n", n)
        form_data.add_field("size", size)
        form_data.add_field("response_format", response_format)
        
        if mask:
            form_data.add_field("mask", await mask.read(), filename=mask.filename, content_type=mask.content_type)
        if user:
            form_data.add_field("user", user)
        
        url = "https://api.openai.com/v1/images/edits"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data, headers=headers) as response:
                result = await response.json()
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=result)
                return result
        
    except Exception as e:
        logger.error(f"Error in image editing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Image variation endpoint
@app.post("/v1/images/variations")
async def image_variations(request: Request):
    """Image variation endpoint"""
    api_key = get_api_key(request)
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Handle multipart form data
        form = await request.form()
        image = form.get("image")
        model = form.get("model", "dall-e-2")
        n = form.get("n", "1")
        response_format = form.get("response_format", "url")
        size = form.get("size", "1024x1024")
        user = form.get("user")
        
        if not image:
            raise HTTPException(status_code=400, detail="Image is required")
        
        # Update usage
        if api_key in api_keys:
            api_keys[api_key]["usage"] += 1
        
        # Prepare form data for OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field("image", await image.read(), filename=image.filename, content_type=image.content_type)
        form_data.add_field("model", model)
        form_data.add_field("n", n)
        form_data.add_field("response_format", response_format)
        form_data.add_field("size", size)
        
        if user:
            form_data.add_field("user", user)
        
        url = "https://api.openai.com/v1/images/variations"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data, headers=headers) as response:
                result = await response.json()
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=result)
                return result
        
    except Exception as e:
        logger.error(f"Error in image variation: {e}")
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
        # Try multiple possible paths for Vercel deployment
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "frontend", "styles.css"),
            os.path.join(os.getcwd(), "frontend", "styles.css"),
            "frontend/styles.css",
            "styles.css"
        ]
        
        css_path = None
        for path in possible_paths:
            if os.path.exists(path):
                css_path = path
                break
        
        if not css_path:
            raise FileNotFoundError("CSS file not found")
            
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
        # Try multiple possible paths for Vercel deployment
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "frontend", "script.js"),
            os.path.join(os.getcwd(), "frontend", "script.js"),
            "frontend/script.js",
            "script.js"
        ]
        
        js_path = None
        for path in possible_paths:
            if os.path.exists(path):
                js_path = path
                break
        
        if not js_path:
            raise FileNotFoundError("JS file not found")
            
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
        # Try multiple possible paths for Vercel deployment
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "frontend", "favicon.ico"),
            os.path.join(os.getcwd(), "frontend", "favicon.ico"),
            "frontend/favicon.ico",
            "favicon.ico"
        ]
        
        favicon_path = None
        for path in possible_paths:
            if os.path.exists(path):
                favicon_path = path
                break
        
        if not favicon_path:
            raise FileNotFoundError("Favicon file not found")
            
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
                "/v1/embeddings",
                "/v1/moderations",
                "/v1/audio/transcriptions",
                "/v1/audio/translations",
                "/v1/images/generations",
                "/v1/images/edits",
                "/v1/images/variations",
                "/api/keys"
            ]
        },
        status_code=404
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
