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
from ....responses import PrettyJSONResponse
from ...constants import DEPENDENCIES
from ....models import ImageRequest
from ....core import ProviderManager
from ....providers import Model, BaseProvider
from ...exceptions import InsufficientCreditsError, NoProviderAvailableError

router = APIRouter()

class ImageHandler:
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

@router.post('/generations', dependencies=DEPENDENCIES, response_model=None)
async def images_generations(
    request: Request,
    data: ImageRequest
) -> PrettyJSONResponse:
    """Generate images from text prompts"""
    try:
        provider = await ImageHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = ImageHandler._get_token_count(data.model)

        # Credit validation removed - API is now fully free

        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.images_generations(
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
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=traceback.format_exc()
        )

@router.post('/upscale', dependencies=DEPENDENCIES, response_model=None)
async def upscale(
    request: Request,
    model: str = Form(...),
    file: UploadFile = File(...)
) -> Response:
    """Upscale an image to higher resolution"""
    try:
        provider = await ImageHandler._get_provider(model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = ImageHandler._get_token_count(model)

        # Credit validation removed - API is now fully free

        request.state.provider = provider
        request.state.provider_name = provider['name']

        return await provider_instance.upscale(
            request,
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
