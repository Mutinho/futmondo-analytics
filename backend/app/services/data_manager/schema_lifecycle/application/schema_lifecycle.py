"""Thin orchestrator for the ``schema-lifecycle`` responsibility (BR1.3).

Delegates to an injected :class:`SchemaLifecycleDataPort`; no SQL (BR1.3).
"""

from typing import Any, Optional

from app.services.data_manager.schema_lifecycle.domain.ports import (
    SchemaLifecycleDataPort,
)


class SchemaLifecycleService:
    """Coordinate schema DDL / championship bootstrap over the port."""

    def __init__(self, port: SchemaLifecycleDataPort) -> None:
        self.port = port

    def init_database(self) -> None:
        return self.port.init_database()

    def reset_database(self) -> None:
        return self.port.reset_database()

    def ensure_championship_exists(
        self,
        championship_id: str,
        name: Optional[str] = None,
        conn: Any = None,
        cursor: Any = None,
    ) -> None:
        return self.port.ensure_championship_exists(
            championship_id, name=name, conn=conn, cursor=cursor
        )

    def ensure_championship_in_transaction(
        self, cursor: Any, championship_id: str, name: Optional[str] = None
    ) -> None:
        return self.port.ensure_championship_in_transaction(cursor, championship_id, name=name)

    def ensure_schema_updates(self) -> None:
        return self.port.ensure_schema_updates()
