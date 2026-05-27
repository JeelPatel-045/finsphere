from fastapi import APIRouter

from app.api.routes.auth          import router as auth_router
from app.api.routes.chat          import router as chat_router
from app.api.routes.dashboard     import router as dashboard_router
from app.api.routes.audit         import router as audit_router
from app.api.routes.forecasting   import router as forecast_router
from app.api.routes.sql_agent     import router as sql_router
from app.api.routes.upload        import router as upload_router
from app.api.routes.agents        import router as agents_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.settings_route import router as settings_router
from app.api.routes.search        import router as search_router
from app.api.routes.reports       import router as reports_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router,          tags=["Auth"])
api_router.include_router(chat_router,          tags=["Chat"])
api_router.include_router(dashboard_router,     tags=["Dashboard"])
api_router.include_router(audit_router,         tags=["Audit"])
api_router.include_router(forecast_router,      tags=["Forecasting"])
api_router.include_router(sql_router,           tags=["SQL Agent"])
api_router.include_router(upload_router,        tags=["Documents"])
api_router.include_router(agents_router,        tags=["Agents"])
api_router.include_router(notifications_router, tags=["Notifications"])
api_router.include_router(settings_router,      tags=["Settings"])
api_router.include_router(search_router,        tags=["Search"])
api_router.include_router(reports_router,       tags=["Reports"])
