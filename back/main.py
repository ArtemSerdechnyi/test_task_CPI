import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from back.app.api.routers import main_router
from back.app.core.config import settings
from back.app.core.exceptions import BadRequestException, InternalServerException
from back.app.services.cpi_parser import germany_historical_cpi_parser


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting app...")
    asyncio.create_task(germany_historical_cpi_parser.parse_into_mapper())
    scheduler.add_job(
        germany_historical_cpi_parser.parse_into_mapper,
        trigger=CronTrigger(hour="*/6", minute=0, timezone="UTC"),
        id="resign_expired_thumbnails",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started.")
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


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BadRequestException)
    async def bad_request_exception_handler(
        _: Request,
        exc: BadRequestException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(InternalServerException)
    async def internal_server_exception_handler(
        _: Request,
        exc: InternalServerException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="CPI",
    )

    _include_router(app)
    _add_middleware(app)
    _register_exception_handlers(app)
    return app


if __name__ == "__main__":
    uvicorn.run(
        "back.main:create_app",
        factory=True,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
    )
