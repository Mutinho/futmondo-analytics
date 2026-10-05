"""Consumer-owned data port for the ``news-articles`` responsibility (BR1.3).

Structural :class:`typing.Protocol` describing ONLY the operations the
news-articles orchestrator consumes; no SQL, no framework (BR1.3). The concrete
:class:`~app.services.data_manager.news_articles.infrastructure.news_articles_adapter.NewsArticlesAdapter`
implements it.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol


class NewsArticlesDataPort(Protocol):
    """Structural type of the persistence surface news-articles consumes."""

    def save_matchday_article(
        self,
        championship_id: str,
        matchday: int,
        article: str,
        summary: Optional[Dict] = None,
        generated_at: Optional[datetime] = None,
    ) -> None:
        """Persist the generated matchday article and optional summary."""
        ...

    def get_matchday_article(self, championship_id: str, matchday: int) -> Optional[Dict[str, Any]]:
        """Retrieve the stored matchday article and metadata (None if absent)."""
        ...

    def save_pressroom_news(self, championship_id: str, news_items: List[Dict]) -> None:
        """Legacy no-op: pressroom news is not kept in the optimized schema."""
        ...

    def get_matchday_data_for_news(self, championship_id: str, matchday: int) -> Dict:
        """Return the comprehensive matchday payload used to generate press news."""
        ...
