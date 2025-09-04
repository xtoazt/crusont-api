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
async def home() -> Dict[str, Any]:
    return {
        'message': 'Welcome to the Crusont API! Basic free AI gateway.',
        'version': '1.0.0',
        'status': 'Free and Open',
        'features': [
            'Chat completions',
            'No restrictions or limits'
        ]
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
async def favicon():
    return {"message": "No favicon available"}

# Add health check endpoint
@app.get('/health')
async def health():
    return {"status": "healthy", "message": "Crusont API is running"}

# Add catch-all for any other routes
@app.get('/{path:path}')
async def catch_all(path: str):
    return {
        "error": "Endpoint not found",
        "path": path,
        "message": "This endpoint is not available in the basic version",
        "available_endpoints": [
            "/",
            "/v1/models", 
            "/v1/chat/completions",
            "/api/",
            "/api/v1/models",
            "/health"
        ]
    }
