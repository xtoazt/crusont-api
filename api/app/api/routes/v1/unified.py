import traceback
from fastapi import (
    APIRouter,
    Request,
    Response,
    UploadFile,
    File,
    Form,
    HTTPException,
    Path
)
from typing import Union, Dict, Any
from pydantic import BaseModel
from ....responses import PrettyJSONResponse, StreamingResponse
from ...constants import DEPENDENCIES
from ....models import (
    ChatRequest, 
    EmbeddingsRequest, 
    ModerationRequest,
    SpeechRequest,
    ImageRequest,
    TextTranslationsRequest
)
from ....core import ProviderManager
from ....providers import Model, BaseProvider
from ...exceptions import InsufficientCreditsError, NoProviderAvailableError
from ....utils import RequestProcessor

router = APIRouter()

# Request models for API key management
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

# Unified handler classes
class UnifiedHandler:
    provider_manager = ProviderManager()
    request_processor = RequestProcessor()

    @classmethod
    async def _get_provider(cls, model: str, vision_required: bool = False, tools_required: bool = False, name: str = '') -> dict:
        if name:
            provider = await cls.provider_manager.get_provider_by_name(name)
        else:
            provider = await cls.provider_manager.get_best_provider(
                model, 
                vision_required=vision_required, 
                tools_required=tools_required
            )
        
        if not provider:
            raise NoProviderAvailableError()
        return provider

    @staticmethod
    def _validate_credits(available_credits: int, required_tokens: int) -> None:
        # Credit validation removed - API is now fully free
        pass

    @staticmethod
    def _get_token_count(model: str) -> int:
        model_instance = Model.get_model(model)
        return model_instance.pricing.price

    @staticmethod
    def _has_vision_requirement(messages) -> bool:
        return any(
            isinstance(message.content, list) and 
            any(content.type == 'image_url' for content in message.content)
            for message in messages
        )

# Chat Completions
@router.post('/chat/completions', dependencies=DEPENDENCIES, response_model=None)
async def chat_completions(
    request: Request,
    data: ChatRequest
) -> Union[PrettyJSONResponse, StreamingResponse]:
    try:
        token_count = UnifiedHandler.request_processor.count_tokens(data)
        request.state.token_count = token_count

        if data.provider_name:
            provider = await UnifiedHandler._get_provider(
                model=data.model,
                name=data.provider_name
            )
        else:
            vision_required = UnifiedHandler._has_vision_requirement(data.messages)
            provider = await UnifiedHandler._get_provider(
                model=data.model,
                vision_required=vision_required,
                tools_required=data.tools
            )
        
        request.state.provider = provider
        request.state.provider_name = provider['name']

        provider_instance = BaseProvider.get_provider_class(provider['name'])

        if not provider_instance:
            raise HTTPException(
                status_code=500,
                detail='Something went wrong when getting the provider class, which turned out to be null. Please try again later.'
            )

        response = await provider_instance.chat_completions(
            request,
            **data.model_dump(
                mode='json',
                exclude_none=True,
                exclude={'provider_name'}
            )
        )

        if response.status_code == 503:
            print(f'{data.model}: No sub-provider available ({provider["name"]})')

        return response
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Embeddings
@router.post('/embeddings', dependencies=DEPENDENCIES, response_model=None)
async def embeddings(
    request: Request,
    data: EmbeddingsRequest
) -> PrettyJSONResponse:
    try:
        provider = await UnifiedHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(data.model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.embeddings(
            request,
            **data.model_dump(mode='json', exclude_none=True)
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Moderations
@router.post('/moderations', dependencies=DEPENDENCIES, response_model=None)
async def moderations(
    request: Request,
    data: ModerationRequest
) -> PrettyJSONResponse:
    try:
        provider = await UnifiedHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(data.model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.moderations(
            request,
            **data.model_dump(mode='json', exclude_none=True)
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Audio Speech
@router.post('/audio/speech', dependencies=DEPENDENCIES, response_model=None)
async def audio_speech(
    request: Request,
    data: SpeechRequest
) -> Response:
    try:
        provider = await UnifiedHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(data.model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.speech(
            request,
            **data.model_dump(mode='json', exclude_none=True)
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Audio Transcriptions
@router.post('/audio/transcriptions', dependencies=DEPENDENCIES, response_model=None)
async def audio_transcriptions(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form(...),
    language: str = Form(None),
    prompt: str = Form(None),
    response_format: str = Form("json"),
    temperature: float = Form(0)
) -> PrettyJSONResponse:
    try:
        provider = await UnifiedHandler._get_provider(model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.transcriptions(
            request,
            file=file,
            model=model,
            language=language,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Audio Translations
@router.post('/audio/translations', dependencies=DEPENDENCIES, response_model=None)
async def audio_translations(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form(...),
    prompt: str = Form(None),
    response_format: str = Form("json"),
    temperature: float = Form(0)
) -> PrettyJSONResponse:
    try:
        provider = await UnifiedHandler._get_provider(model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.translations(
            request,
            file=file,
            model=model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Image Generations
@router.post('/images/generations', dependencies=DEPENDENCIES, response_model=None)
async def images_generations(
    request: Request,
    data: ImageRequest
) -> PrettyJSONResponse:
    try:
        provider = await UnifiedHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(data.model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.image_generations(
            request,
            **data.model_dump(mode='json', exclude_none=True)
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Image Upscale
@router.post('/images/upscale', dependencies=DEPENDENCIES, response_model=None)
async def images_upscale(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form(...),
    n: int = Form(1),
    size: str = Form("1024x1024"),
    response_format: str = Form("url"),
    user: str = Form(None)
) -> PrettyJSONResponse:
    try:
        provider = await UnifiedHandler._get_provider(model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.image_upscale(
            request,
            file=file,
            model=model,
            n=n,
            size=size,
            response_format=response_format,
            user=user
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Text Translations
@router.post('/text/translations', dependencies=DEPENDENCIES, response_model=None)
async def text_translations(
    request: Request,
    data: TextTranslationsRequest
) -> PrettyJSONResponse:
    try:
        provider = await UnifiedHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = UnifiedHandler._get_token_count(data.model)
        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.text_translations(
            request,
            **data.model_dump(mode='json', exclude_none=True)
        )
        
    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

# Models endpoint
@router.get('/models', response_class=PrettyJSONResponse)
async def models() -> Dict[str, Any]:
    return {
        'an_easier_overview_available_here': 'https://docs.crusont.com/models',
        'object': 'list',
        'data': Model.all_to_json()
    }

# API Key Management
@router.get('/keys', dependencies=DEPENDENCIES)
async def get_api_keys(request: Request) -> Dict[str, Any]:
    try:
        from ....core.db.managers.user_manager import UserManager
        user_manager = UserManager()
        
        user_id = request.state.user['user_id']
        api_keys = await user_manager.get_user_api_keys(user_id)
        
        return {
            'object': 'list',
            'data': [
                {
                    'id': str(key['_id']),
                    'name': key.get('name', 'Unnamed Key'),
                    'key': key['key'],
                    'created_at': key['created_at'],
                    'last_used': key.get('last_used'),
                    'is_active': key.get('is_active', True)
                }
                for key in api_keys
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve API keys: {str(e)}")

@router.post('/keys', dependencies=DEPENDENCIES)
async def create_api_key(
    request: Request,
    data: CreateApiKeyRequest
) -> ApiKeyResponse:
    try:
        from ....core.db.managers.user_manager import UserManager
        user_manager = UserManager()
        
        user_id = request.state.user['user_id']
        api_key = await user_manager.create_api_key(user_id, data.name)
        
        return ApiKeyResponse(
            id=str(api_key['_id']),
            name=api_key['name'],
            key=api_key['key'],
            created_at=api_key['created_at'],
            last_used=api_key.get('last_used')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")

@router.delete('/keys/{key_id}', dependencies=DEPENDENCIES)
async def delete_api_key(
    request: Request,
    key_id: str = Path(...)
) -> Dict[str, Any]:
    try:
        from ....core.db.managers.user_manager import UserManager
        user_manager = UserManager()
        
        user_id = request.state.user['user_id']
        success = await user_manager.delete_api_key(user_id, key_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {
            'object': 'api_key.deleted',
            'id': key_id,
            'deleted': True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete API key: {str(e)}")
