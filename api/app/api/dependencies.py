import time
from fastapi import Request, HTTPException
from typing import Optional
from ..core import UserManager
from ..providers import Model

class AuthenticationHandler:
    user_manager = UserManager()

    @staticmethod
    async def _get_api_key(token: Optional[str]) -> str:
        if not token:
            raise HTTPException(
                detail=(
                    'No API key was provided in the request. '
                    'Please include your API key in the Authorization header as "Bearer <your_key>". '
                    'If you don\'t have an API key, get one at: https://discord.gg/crusont'
                ),
                status_code=401
            )
        return token.replace('Bearer ', '')

    @classmethod
    async def _validate_user(cls, key: str) -> dict:
        user = await cls.user_manager.get_user(key=key)
        if not user:
            raise HTTPException(
                detail=(
                    'The provided API key was not found in our system. '
                    'Please check that you entered it correctly. '
                    'If you need a valid API key, get one at: https://discord.gg/crusont'
                ),
                status_code=401
            )
        
        if user['banned']:
            raise HTTPException(
                detail=(
                    'Your API key has been banned from accessing the service. '
                    'This may be due to violation of our terms of service, abuse, leaving the server, etc. '
                    'To appeal your ban, please visit: https://discord.gg/crusont'
                ),
                status_code=403
            )
        
        # Update last used timestamp for the API key
        await cls.user_manager.update_api_key_last_used(key)
        
        return user

class UserAccessHandler:
    user_manager = UserManager()

    @classmethod
    async def _check_premium_status(cls, user: dict) -> None:
        # Premium status checking removed - API is now fully free
        pass

    @classmethod
    async def _validate_ip(cls, request: Request, user: dict) -> None:
        # IP validation removed - API is now fully open and free
        pass

class RequestValidator:
    @staticmethod
    async def _get_request_body(request: Request) -> dict:
        try:
            if request.headers.get('Content-Type') == 'application/json':
                body = await request.json()
            elif request.headers.get('Content-Type').startswith('multipart/form-data'):
                body = await request.form()
            
            if not body:
                raise ValueError('Invalid body.')
            
            return body
        except Exception:
            raise HTTPException(
                detail=(
                    'An error occured while parsing your payload, '
                    'or you didn\'t provider a "Content-Type" header. '
                    'Review your request and try again.'
                ),
                status_code=400
            )

    @staticmethod
    def _validate_model_access(
        model: str,
        endpoint: str,
        voice: Optional[str],
        user_tier: int
    ) -> None:
        model_instance = Model.get_model(model)

        if not model_instance:
            raise HTTPException(
                detail=(
                    f'The model `{model}` does not exist. Please check our model documentation at '
                    'https://docs.crusont.com/models for a list of available models.'
                ),
                status_code=400
            )
        
        is_endpoint_mismatch = (
            (isinstance(model_instance.endpoint, str) and model_instance.endpoint != endpoint) or
            (not isinstance(model_instance.endpoint, str) and endpoint not in model_instance.endpoint)
        )

        if is_endpoint_mismatch:
            raise HTTPException(
                status_code=400,
                detail=(
                    f'The model `{model}` cannot be used with this endpoint ({endpoint}). '
                    f'This model should be used with {model_instance.endpoint} instead. '
                    'Please check our documentation at https://docs.crusont.com/models '
                    'for proper model usage.'
                )
            )

        if endpoint == '/v1/audio/speech' and voice:
            if voice not in model_instance.voices:
                raise HTTPException(
                    detail=(
                        f'The voice `{voice}` is not available for this model. '
                        'Please check our documentation at https://docs.crusont.com/models '
                        'for a list of supported voices.'
                    ),
                    status_code=400
                )

        # All models are now free and accessible - no restrictions
        pass

async def authentication(request: Request) -> None:
    key = await AuthenticationHandler._get_api_key(
        request.headers.get('Authorization')
    )
    user = await AuthenticationHandler._validate_user(key)
    request.state.user = user

async def validate_user_access(request: Request) -> None:
    user = request.state.user
    await UserAccessHandler._check_premium_status(user)
    await UserAccessHandler._validate_ip(request, user)

async def validate_request_body(request: Request) -> None:
    body = await RequestValidator._get_request_body(request)
    
    RequestValidator._validate_model_access(
        model=body.get('model'),
        endpoint=request.url.path,
        voice=body.get('voice'),
        user_tier=request.state.user.get('premium_tier', 0)
    )