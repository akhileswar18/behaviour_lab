from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.logging import configure_logging
from app.api.routes import agents, health, relationships, scenarios, simulation, timeline
from app.persistence.init_db import init_db
from app.schemas.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Behavior Lab API", version="0.1.0", lifespan=lifespan)
app.include_router(health.router)
app.include_router(scenarios.router)
app.include_router(simulation.router)
app.include_router(timeline.router)
app.include_router(agents.router)
app.include_router(relationships.router)

logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
