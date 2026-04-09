import logging
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import require_role
from app.models.enums import UserRole, Platform
from app.schemas.validators import validate_date_range
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connectors", tags=["Data Connectors"])


@router.get("/health")
async def connector_health(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    logger.info("Connector health check requested by user_id=%s", user.id)
    service = IngestionService(db)
    return await service.check_health()


@router.post("/ingest")
async def trigger_ingestion(
    start_date: date = Query(...),
    end_date: date = Query(...),
    platforms: list[Platform] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    validate_date_range(start_date, end_date)
    logger.info("Ingestion triggered by user_id=%s for %s to %s", user.id, start_date, end_date)
    service = IngestionService(db)
    results = await service.ingest_all(start_date, end_date, platforms)
    return {"status": "completed", "records_ingested": results}
