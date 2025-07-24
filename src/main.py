from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from api.routes import file
from exceptions.handler import ExceptionHandler
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from infrastructure.minio import minioStorage
from api.responses.response import ErrorResponse
import logging
import traceback
import sys

# Configure logging to ensure it outputs to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Test logging to verify configuration
logger.info("=== FASTAPI APPLICATION STARTING ===")
logger.info("Logging configuration initialized")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup, run the bucket setup logic.
    # This happens after the event loop starts but before we accept requests.
    try:
        minioStorage.setup_buckets()
        logger.info("MinIO buckets and policies configured.")
    except Exception as e:
        logger.error(f"Failed to setup MinIO buckets: {str(e)}")
        raise
    yield
    # Code to run on shutdown could go here if needed.


def create_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # Add CORS middleware FIRST
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"], #allow frontend to access the backend
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global exception handler to ensure CORS headers are always present
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception handler caught: {str(exc)}\n{traceback.format_exc()}")
        
        # Create a JSONResponse with CORS headers
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error", "detail": str(exc)}
        )
        
        # Manually add CORS headers to ensure they're present
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response
    
    app.include_router(file.router)
    ExceptionHandler(app)
    return app


app = create_application()
