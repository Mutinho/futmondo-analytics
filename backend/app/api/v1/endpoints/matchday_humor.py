from fastapi import APIRouter, Depends, HTTPException, Query

from app.core import config
from app.services.matchday_humor_service import MatchdayHumorService

router = APIRouter(prefix="/humor", tags=["humor"])


def get_service() -> MatchdayHumorService:
    return MatchdayHumorService()


@router.get("/article")
async def get_matchday_article(
    matchday: int = Query(..., ge=1, le=38, description="Jornada objetivo."),
    championship_id: str = Query(default=config.CHAMPIONSHIP_ID, description="Championship ID"),
    force_refresh: bool = Query(False, description="Regenerar el artículo incluso si está cacheado"),
    service: MatchdayHumorService = Depends(get_service)
):
    try:
        payload = service.get_or_generate_article(
            championship_id=championship_id,
            matchday=matchday,
            force_refresh=force_refresh
        )
        return {"success": True, "data": payload}
    except Exception as exc:  # pragma: no cover - runtime path
        raise HTTPException(status_code=500, detail=str(exc))

