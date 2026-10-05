"""Thin orchestrator for the ``news-articles`` responsibility (BR1.3).

Delegates to an injected :class:`NewsArticlesDataPort`; contains no SQL (BR1.3).
Behavior is identical to the former ``DataManagerV2`` methods.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.news_articles.domain.ports import NewsArticlesDataPort


class NewsArticlesService:
    """Coordinate news-articles persistence over a ``NewsArticlesDataPort``."""

    def __init__(self, port: NewsArticlesDataPort) -> None:
        self.port = port

    def save_matchday_article(
        self,
        championship_id: str,
        matchday: int,
        article: str,
        summary: Optional[Dict] = None,
        generated_at: Optional[datetime] = None,
    ) -> None:
        return self.port.save_matchday_article(
            championship_id, matchday, article, summary=summary, generated_at=generated_at
        )

    def get_matchday_article(self, championship_id: str, matchday: int) -> Optional[Dict[str, Any]]:
        return self.port.get_matchday_article(championship_id, matchday)

    def save_pressroom_news(self, championship_id: str, news_items: List[Dict]) -> None:
        return self.port.save_pressroom_news(championship_id, news_items)

    def get_matchday_data_for_news(self, championship_id: str, matchday: int) -> Dict:
        return self.port.get_matchday_data_for_news(championship_id, matchday)
