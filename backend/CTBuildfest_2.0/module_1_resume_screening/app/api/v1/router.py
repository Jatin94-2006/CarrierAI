from fastapi import APIRouter
from app.api.v1.routes.resume import router as resume_router
from app.api.v1.routes.job import router as job_router
from app.api.v1.routes.screening import router as screening_router
from app.api.v1.routes.ranking import router as ranking_router
from app.api.v1.routes.integration import router as integration_router

api_v1_router = APIRouter()

api_v1_router.include_router(resume_router)
api_v1_router.include_router(job_router)
api_v1_router.include_router(screening_router)
api_v1_router.include_router(ranking_router)
api_v1_router.include_router(integration_router)
