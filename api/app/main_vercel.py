"""
Vercel-compatible version of the main FastAPI app
This version removes the lifespan function and background tasks that don't work well in serverless
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from .providers import BaseProvider
from .errors import ExceptionHandler
from .utils import RequestProcessor, RouteLoader

# Initialize components without background tasks
base_provider = BaseProvider()
request_processor = RequestProcessor()

# Create FastAPI app without lifespan
app = FastAPI(
    docs_url=None,
    redoc_url=None
)

app.state.limiter = Limiter(
    key_func=request_processor.get_api_key,
    default_limits=[
        '2/second',
        '30/minute'
    ]
)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

ExceptionHandler.setup(app)

# Load routes
RouteLoader.load(
    app=app,
    base_dir='app/api/routes'
)

# Initialize providers synchronously for Vercel
@app.on_event("startup")
async def startup_event():
    """Initialize providers on startup"""
    try:
        await base_provider.import_modules()
        await base_provider.sync_to_db()
    except Exception as e:
        print(f"Warning: Failed to initialize providers: {e}")
        # Continue without failing the app startup
