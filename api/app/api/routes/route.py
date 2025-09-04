from fastapi import APIRouter
from typing import Dict, Any
from ...responses import PrettyJSONResponse

router = APIRouter()

@router.get('/', response_class=PrettyJSONResponse)
async def home() -> Dict[str, Any]:
    return {
        'message': 'Welcome to the Crusont API! Fully free and open AI gateway.',
        'version': '1.0.0',
        'status': 'Free and Open',
        'features': [
            'Multi-provider AI access',
            'Multiple API keys per user',
            'No rate limits or restrictions',
            'All models free and accessible',
            'No IP locks or premium tiers',
            'Chat completions, embeddings, moderation',
            'Audio and image processing',
            'Text translation services'
        ],
        'documentation': 'https://docs.crusont.com',
        'github': 'https://github.com/crusont/api'
    }