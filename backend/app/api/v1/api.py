from fastapi import APIRouter
from app.api.v1.endpoints import tariff, export, stats, calculations, comparisons, catalogs, watchlists, notifications, subscriptions, webhooks, chat, cashflow, compliance_tools, action_list, sourcing, scenarios, analyses
from app.api.endpoints import auth, admin

api_router = APIRouter()
api_router.include_router(tariff.router, prefix="/tariff", tags=["tariff"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(calculations.router, prefix="/calculations", tags=["calculations"])
api_router.include_router(comparisons.router, prefix="/comparisons", tags=["comparisons"])
api_router.include_router(catalogs.router, prefix="/catalogs", tags=["catalogs"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(cashflow.router, prefix="/cashflow", tags=["cashflow"])
api_router.include_router(compliance_tools.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(action_list.router, prefix="/action-list", tags=["action-list"])
api_router.include_router(sourcing.router, prefix="/sourcing", tags=["sourcing"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])