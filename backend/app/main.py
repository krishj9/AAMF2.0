from fastapi import FastAPI

from app.api.routes.approvals import router as approvals_router
from app.api.routes.health import router as health_router
from app.api.routes.rebalance import router as rebalance_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Personal portfolio decision-support API.",
    )
    app.include_router(approvals_router)
    app.include_router(health_router)
    app.include_router(rebalance_router)
    return app


app = create_app()
