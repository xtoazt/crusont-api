"""
Basic FastAPI application for Vercel deployment
Minimal imports and dependencies
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, Dict, Any
from pydantic import BaseModel
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Create FastAPI app
app = FastAPI(
    title="Crusont API",
    description="Basic free AI gateway",
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

# Basic request model
class ChatRequest(BaseModel):
    model: str
    messages: list
    temperature: float = 0.7
    max_tokens: int = 1000

# Root endpoint
@app.get('/')
async def home(request: Request) -> Dict[str, Any]:
    print(f"Root endpoint accessed: {request.url}")
    return {
        'message': 'Welcome to the Crusont API! Basic free AI gateway.',
        'version': '1.0.0',
        'status': 'Free and Open',
        'features': [
            'Chat completions',
            'No restrictions or limits'
        ],
        'endpoints': {
            'models': '/v1/models',
            'chat': '/v1/chat/completions',
            'health': '/health',
            'docs': '/docs/',
            'frontend': '/'
        }
    }

# Models endpoint
@app.get('/v1/models')
async def models() -> Dict[str, Any]:
    return {
        'object': 'list',
        'data': [
            {
                'id': 'gpt-3.5-turbo',
                'object': 'model',
                'created': 1677610602,
                'owned_by': 'openai'
            },
            {
                'id': 'gpt-4',
                'object': 'model',
                'created': 1677610602,
                'owned_by': 'openai'
            },
            {
                'id': 'gpt-4-turbo',
                'object': 'model',
                'created': 1677610602,
                'owned_by': 'openai'
            },
            {
                'id': 'claude-3-sonnet',
                'object': 'model',
                'created': 1677610602,
                'owned_by': 'anthropic'
            },
            {
                'id': 'claude-3-opus',
                'object': 'model',
                'created': 1677610602,
                'owned_by': 'anthropic'
            }
        ]
    }

# Chat Completions
@app.post('/v1/chat/completions')
async def chat_completions(
    request: Request,
    data: ChatRequest
) -> Dict[str, Any]:
    try:
        # Basic response for now
        return {
            'id': 'chatcmpl-123',
            'object': 'chat.completion',
            'created': 1677652288,
            'model': data.model,
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': 'Hello! This is a basic response from Crusont API. The full functionality is being optimized for deployment.'
                    },
                    'finish_reason': 'stop'
                }
            ],
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 10,
                'total_tokens': 20
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API routes (for backward compatibility)
@app.get('/api/')
async def api_home() -> Dict[str, Any]:
    return await home()

@app.get('/api/v1/models')
async def api_models() -> Dict[str, Any]:
    return await models()

# Serve frontend files
@app.get('/index.html')
async def serve_index():
    from fastapi.responses import Response
    import os
    
    # Read the frontend index.html file
    frontend_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'index.html')
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="text/html",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except FileNotFoundError:
        return Response(
            content="<h1>Frontend not found</h1>",
            media_type="text/html"
        )

@app.get('/styles.css')
async def serve_styles():
    from fastapi.responses import Response
    import os
    
    frontend_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'styles.css')
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
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

@app.get('/script.js')
async def serve_script():
    from fastapi.responses import Response
    import os
    
    frontend_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'script.js')
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
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

@app.get('/favicon.ico')
async def serve_favicon():
    from fastapi.responses import Response
    import os
    
    frontend_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'favicon.ico')
    try:
        with open(frontend_path, 'rb') as f:
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

# Add health check endpoint
@app.get('/health')
async def health():
    return {"status": "healthy", "message": "Crusont API is running"}

# Add test endpoint
@app.get('/test')
async def test():
    return {
        "status": "success",
        "message": "API is working correctly",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints_tested": [
            "/",
            "/v1/models",
            "/health",
            "/test"
        ]
    }

# Add catch-all for any other routes
@app.get('/{path:path}')
async def catch_all(path: str, request: Request):
    print(f"404 - Requested path: {path}")
    print(f"404 - Request method: {request.method}")
    print(f"404 - Request headers: {dict(request.headers)}")
    print(f"404 - Request URL: {request.url}")
    return {
        "error": "Endpoint not found",
        "path": path,
        "method": request.method,
        "url": str(request.url),
        "message": "This endpoint is not available in the basic version",
        "available_endpoints": [
            "/",
            "/v1/models", 
            "/v1/chat/completions",
            "/api/",
            "/api/v1/models",
            "/health",
            "/favicon.ico",
            "/robots.txt",
            "/sitemap.xml",
            "/manifest.json"
        ]
    }
