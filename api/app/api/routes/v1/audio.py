import traceback
from fastapi import (
    APIRouter,
    Request,
    Response,
    UploadFile,
    File,
    Form,
    HTTPException
)
from typing import Union
from ....responses import PrettyJSONResponse
from ...constants import DEPENDENCIES
from ....models import SpeechRequest
from ....core import ProviderManager
from ....providers import Model, BaseProvider
from ...exceptions import InsufficientCreditsError, NoProviderAvailableError

router = APIRouter()

class AudioHandler:
    provider_manager = ProviderManager()

    @classmethod
    async def _get_provider(cls, model: str) -> dict:
        provider = await cls.provider_manager.get_best_provider(model)
        if not provider:
            raise NoProviderAvailableError()
        return provider

    @staticmethod
    def _validate_credits(
        available_credits: int,
        required_tokens: int
    ) -> None:
        # Credit validation removed - API is now fully free
        pass

    @staticmethod
    def _get_token_count(model: str) -> int:
        model_instance = Model.get_model(model)
        return model_instance.pricing.price

@router.post('/speech', dependencies=DEPENDENCIES, response_model=None)
async def audio_speech(
    request: Request,
    data: SpeechRequest
) -> Response:
    """Generate speech from text"""
    try:
        provider = await AudioHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = AudioHandler._get_token_count(data.model)

        # Credit validation removed - API is now fully free

        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.audio_speech(
            request,
            **data.model_dump(mode='json')
        )

    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=traceback.format_exc()
        )

@router.post('/transcriptions', dependencies=DEPENDENCIES, response_model=None)
async def audio_transcriptions(
    request: Request,
    model: str = Form(...),
    file: UploadFile = File(...)
) -> Response:
    """Transcribe audio to text"""
    try:
        provider = await AudioHandler._get_provider(model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = AudioHandler._get_token_count(model=model)

        # Credit validation removed - API is now fully free

        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.audio_transcriptions(
            request,
            model,
            file
        )

    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=traceback.format_exc()
        )

@router.post('/translations', dependencies=DEPENDENCIES, response_model=None)
async def audio_translations(
    request: Request,
    model: str = Form(...),
    file: UploadFile = File(...)
) -> Response:
    """Translate audio to text in another language"""
    try:
        provider = await AudioHandler._get_provider(model)

        token_count = AudioHandler._get_token_count(model=model)

        # Credit validation removed - API is now fully free

        provider_instance = BaseProvider.get_provider_class(provider['name'])

        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.audio_translations(
            request,
            model,
            file
        )

    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=traceback.format_exc()
        )
