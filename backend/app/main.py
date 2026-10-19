from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.routers import ai, experiments, lessons, progress, tokenize


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="ExplodeAI API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origin_list,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type", "X-Learner-Id"],
    )

    @app.get("/api/health", tags=["health"])
    def health():
        return {"status": "ok"}

    for r in (lessons.router, experiments.router, tokenize.router, progress.router, ai.router):
        app.include_router(r)
    return app


app = create_app()
