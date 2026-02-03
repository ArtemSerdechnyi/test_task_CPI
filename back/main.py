from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from loguru import logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from back.app.api.routers import main_router
from back.app.core.config import settings
from back.app.services.cpi_parser import germany_historical_cpi_parser


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting app...")
    await germany_historical_cpi_parser.parse_into_mapper()
    yield
    logger.info("Application stopped.")


def _include_router(app: FastAPI) -> None:
    app.include_router(main_router.router)


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
        title="CPI",
    )

    _include_router(app)
    _add_middleware(app)
    return app


if __name__ == "__main__":
    uvicorn.run(
        "back.main:create_app",
        factory=True,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
    )
