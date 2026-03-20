from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.logging import configure_logging
from app.api.routes import (
    agents,
    analytics_agents,
    analytics_social,
    analytics_world,
    goals,
    health,
    relationships,
    resources,
    scenarios,
    simulation,
    timeline,
    world_rest,
    world_ws,
    zones,
)
from app.persistence.init_db import init_db
from app.schemas.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Behavior Lab API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(scenarios.router)
app.include_router(simulation.router)
app.include_router(timeline.router)
app.include_router(agents.router)
app.include_router(analytics_agents.router)
app.include_router(analytics_social.router)
app.include_router(analytics_world.router)
app.include_router(relationships.router)
app.include_router(goals.router)
app.include_router(zones.router)
app.include_router(resources.router)
app.include_router(world_rest.router)
app.include_router(world_ws.router)

logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
