"""Consumer-owned data port for the ``schema-lifecycle`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3). This is the
most-coupled responsibility (schema DDL + championship bootstrap), extracted
last. ``__init__`` stays on the facade (object construction) and delegates its
schema calls here.
"""

from typing import Any, Optional, Protocol


class SchemaLifecycleDataPort(Protocol):
    """Structural type of the surface schema-lifecycle consumes."""

    def init_database(self) -> None:
        """Create the optimized historical schema (drops + recreates tables)."""
        ...

    def reset_database(self) -> None:
        """Drop every table and recreate the schema."""
        ...

    def ensure_championship_exists(
        self,
        championship_id: str,
        name: Optional[str] = None,
        conn: Any = None,
        cursor: Any = None,
    ) -> None:
        """Ensure a championship row exists (FK bootstrap)."""
        ...

    def ensure_championship_in_transaction(
        self, cursor: Any, championship_id: str, name: Optional[str] = None
    ) -> None:
        """Ensure a championship row exists using the provided cursor."""
        ...

    def ensure_schema_updates(self) -> None:
        """Create newer tables/indexes without a full reset."""
        ...
