import traceback
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import List, Dict, Any
from ....responses import PrettyJSONResponse
from ...constants import DEPENDENCIES
from ....core import UserManager
from ....models import CreateApiKeyRequest, DeleteApiKeyRequest
from pydantic import BaseModel

router = APIRouter()

class CreateApiKeyRequest(BaseModel):
    name: str = "Default Key"

class DeleteApiKeyRequest(BaseModel):
    key_id: str

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key: str
    created_at: float
    last_used: float = None

@router.get('/keys', dependencies=DEPENDENCIES, response_class=PrettyJSONResponse)
async def get_api_keys(request: Request) -> Dict[str, Any]:
    """Get all API keys for the authenticated user"""
    try:
        user = request.state.user
        user_manager = UserManager()
        
        api_keys = await user_manager.get_user_api_keys(user['user_id'])
        
        # Format the response
        formatted_keys = []
        for key in api_keys:
            formatted_keys.append({
                'id': str(key['_id']),
                'name': key['name'],
                'key': key['key'],
                'created_at': key['created_at'],
                'last_used': key.get('last_used')
            })
        
        return {
            'object': 'list',
            'data': formatted_keys,
            'count': len(formatted_keys)
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve API keys: {str(e)}"
        )

@router.post('/keys', dependencies=DEPENDENCIES, response_class=PrettyJSONResponse)
async def create_api_key(
    request: Request,
    data: CreateApiKeyRequest
) -> Dict[str, Any]:
    """Create a new API key for the authenticated user"""
    try:
        user = request.state.user
        user_manager = UserManager()
        
        # Create the new API key
        api_key = await user_manager.create_api_key(
            user_id=user['user_id'],
            name=data.name
        )
        
        return {
            'object': 'api_key',
            'id': str(api_key['_id']),
            'name': api_key['name'],
            'key': api_key['key'],
            'created_at': api_key['created_at'],
            'message': 'API key created successfully. Store it securely as it will not be shown again.'
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create API key: {str(e)}"
        )

@router.delete('/keys/{key_id}', dependencies=DEPENDENCIES, response_class=PrettyJSONResponse)
async def delete_api_key(
    request: Request,
    key_id: str
) -> Dict[str, Any]:
    """Delete an API key for the authenticated user"""
    try:
        user = request.state.user
        user_manager = UserManager()
        
        # Delete the API key
        success = await user_manager.delete_api_key(
            user_id=user['user_id'],
            key_id=key_id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="API key not found or you don't have permission to delete it"
            )
        
        return {
            'object': 'deleted',
            'id': key_id,
            'deleted': True,
            'message': 'API key deleted successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete API key: {str(e)}"
        )
