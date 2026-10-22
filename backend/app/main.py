from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.routers import agent, ai, attend, embed, experiments, lessons, progress, tokenize, tutor


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

    routers = (lessons.router, experiments.router, tokenize.router, embed.router, attend.router, agent.router,
               progress.router, ai.router, tutor.router)
    for r in routers:
        app.include_router(r)
    return app


app = create_app()
