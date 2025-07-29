from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from api.routes import file, appointment
from exceptions.handler import ExceptionHandler
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from infrastructure.minio import minioStorage
from api.responses.response import ErrorResponse
import logging
import traceback
import sys
from infrastructure.db.mysql import mysql
from services.appointment_service import AppointmentService
from repositories.appointment_repository import AppointmentRepo

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
    # On startup, run the bucket setup logic and seed the database.
    try:
        minioStorage.setup_buckets()
        logger.info("MinIO buckets and policies configured.")
        
        # Seed the database with initial appointments
        db_session = next(mysql.get_db())
        appointment_repo = AppointmentRepo(db=db_session)
        appointment_service = AppointmentService(repo=appointment_repo)
        appointment_service.seed_appointments()
        logger.info("Database seeded with initial appointments.")

    except Exception as e:
        logger.error(f"Failed during application startup: {str(e)}")
        raise
    finally:
        db_session.close()
        
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
    app.include_router(appointment.router)
    ExceptionHandler(app)
    return app


app = create_application()
