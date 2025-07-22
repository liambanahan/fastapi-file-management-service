from fastapi import FastAPI
from api.routes import file
from exceptions.handler import ExceptionHandler
from fastapi.middleware.cors import CORSMiddleware

def create_application() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"], #allow frontend to access the backend
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(file.router)
    ExceptionHandler(app)
    return app

app = create_application()
