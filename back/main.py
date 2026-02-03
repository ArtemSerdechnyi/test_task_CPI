from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from loguru import logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from back.app.core.config import settings


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

def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="COA_API",
    )

    _include_router(app)
    _add_middleware(app)

if __name__ == "__main__":
    uvicorn.run(
        "back.main:create_app",
        factory=True,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
    )
