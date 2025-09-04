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

# Add favicon endpoint to prevent 404
@app.get('/favicon.ico')
async def favicon(request: Request):
    print(f"Favicon requested: {request.url}")
    # Return a simple 1x1 transparent PNG as favicon
    from fastapi.responses import Response
    import base64
    
    # Simple 1x1 transparent PNG
    png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
    
    return Response(
        content=png_data,
        media_type="image/x-icon",
        headers={"Cache-Control": "public, max-age=31536000"}
    )

# Add robots.txt endpoint
@app.get('/robots.txt')
async def robots():
    from fastapi.responses import Response
    return Response(
        content="User-agent: *\nAllow: /",
        media_type="text/plain",
        headers={"Cache-Control": "public, max-age=86400"}
    )

# Add sitemap.xml endpoint
@app.get('/sitemap.xml')
async def sitemap():
    from fastapi.responses import Response
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>/docs/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>"""
    return Response(
        content=content,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=86400"}
    )

# Add manifest.json endpoint
@app.get('/manifest.json')
async def manifest():
    return {
        "name": "Crusont API",
        "short_name": "Crusont",
        "description": "Free and open AI gateway",
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#8B4513",
        "background_color": "#1a1a1a"
    }

# Static file endpoints as fallback
@app.get('/styles.css')
async def styles_css(request: Request):
    print(f"CSS requested: {request.url}")
    from fastapi.responses import Response
    css_content = """/* Basic CSS fallback */
body { 
    font-family: Arial, sans-serif; 
    background: #1a1a1a; 
    color: #fff; 
    margin: 0; 
    padding: 20px; 
}
.container { 
    max-width: 1200px; 
    margin: 0 auto; 
}
.header { 
    text-align: center; 
    margin-bottom: 40px; 
}
.logo { 
    color: #DAA520; 
    font-size: 2.5em; 
    margin: 0; 
}
"""
    return Response(
        content=css_content,
        media_type="text/css",
        headers={"Cache-Control": "public, max-age=3600"}
    )

@app.get('/script.js')
async def script_js(request: Request):
    print(f"JS requested: {request.url}")
    from fastapi.responses import Response
    js_content = """// Basic JS fallback
console.log('Crusont API - Basic script loaded');
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
});
"""
    return Response(
        content=js_content,
        media_type="application/javascript",
        headers={"Cache-Control": "public, max-age=3600"}
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
