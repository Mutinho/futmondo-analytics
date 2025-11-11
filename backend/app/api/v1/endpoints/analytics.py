"""Analytics endpoints exposing advanced championship insights."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.services.analytics_service import AnalyticsService
from app.core.config import CHAMPIONSHIP_ID


def get_service() -> AnalyticsService:
    return AnalyticsService()


router = APIRouter()


@router.get("/championship/trends")
async def championship_trends(
    window: int = Query(default=5, ge=1, le=38),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_championship_trends(championship_id=championship_id, window=window)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/championship/custom-classification")
async def championship_custom_classification(
    window: Optional[int] = Query(default=5, ge=1, le=38),
    exclude_matchday: Optional[List[int]] = Query(default=None),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_championship_custom_classification(
            championship_id=championship_id,
            window=window,
            exclude_matchdays=exclude_matchday
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/championship/heatmap")
async def championship_heatmap(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_championship_heatmap(championship_id=championship_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/players/form")
async def player_form(
    window: int = Query(default=5, ge=1, le=10),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_player_form(championship_id=championship_id, window=window)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/players/value-trend")
async def player_value_trend(
    window_days: int = Query(default=30, ge=1, le=180),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_player_value_trend(championship_id=championship_id, window=window_days)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/users/consistency")
async def user_consistency(
    window: int = Query(default=10, ge=1, le=38),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_user_consistency(championship_id=championship_id, window=window)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/users/market-activity")
async def user_market_activity(
    window_days: int = Query(default=30, ge=1, le=120),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_user_market_activity(championship_id=championship_id, window_days=window_days)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/market/watchlist")
async def market_watchlist(
    limit: int = Query(default=20, ge=1, le=100),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_market_watchlist(championship_id=championship_id, limit=limit)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/clauses/network")
async def clause_network(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_clause_network(championship_id=championship_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/opportunities/streaks")
async def opportunity_streaks(
    min_streak: int = Query(default=3, ge=2, le=10),
    threshold: float = Query(default=6.0, ge=0),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_opportunity_streaks(championship_id=championship_id, min_streak=min_streak, threshold=threshold)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/projections/matchday")
async def matchday_projections(
    matchday: Optional[int] = Query(default=None, ge=1, le=38),
    window: int = Query(default=5, ge=1, le=10),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_matchday_projections(championship_id=championship_id, matchday=matchday, window=window)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


