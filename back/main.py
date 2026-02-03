from contextlib import asynccontextmanager
from typing import AsyncIterator

from loguru import logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting app...")
    yield
    logger.info("Application stopped.")


def _include_router(app: FastAPI) -> None:
    pass

def _add_middleware(app: FastAPI) -> None:
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_URLS if settings.FRONTEND_URLS else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

settings = Settings()
