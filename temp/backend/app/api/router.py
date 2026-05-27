from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.audit import router as audit_router
from app.api.routes.forecasting import router as forecasting_router
from app.api.routes.sql_agent import router as sql_router
from app.api.routes.upload import router as upload_router
from app.api.routes.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api")

api_router.include_router(chat_router)
api_router.include_router(audit_router)
api_router.include_router(forecasting_router)
api_router.include_router(sql_router)
api_router.include_router(upload_router)
api_router.include_router(dashboard_router)