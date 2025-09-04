from fastapi import APIRouter
from typing import Dict, Any
from ...responses import PrettyJSONResponse

router = APIRouter()

@router.get('/', response_class=PrettyJSONResponse)
async def home() -> Dict[str, Any]:
    return {
        'message': 'Welcome to the Crusont API! Documentation is available at https://docs.crusont.com',
        'version': '1.0.0',
        'features': [
            'Multi-provider AI access',
            'Multiple API keys per user',
            'Rate limiting and credit management',
            'Chat completions, embeddings, moderation',
            'Audio and image processing',
            'Text translation services'
        ]
    }