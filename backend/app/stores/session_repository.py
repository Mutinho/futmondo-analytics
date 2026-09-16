"""Durable-session persistence layer (u1-durable-session).

Narrow repository layer for the two durable-session entities:

* ``user_session`` (entity ``UserSession``) — the durable, restart-surviving
  record of an authenticated Futmondo session, keyed by app ``user_id``.
* ``protected_credential`` (entity ``ProtectedCredential``) — the encrypted
  re-auth handle used to rebuild a session after a restart. The cleartext
  password is NEVER stored here; only ``protected_material`` (ciphertext) and a
  ``scheme`` tag live in this table (FR5.1 / NFR1 / BR1.4).

Design constraints:

* The database is the authority for state and concurrency; the in-memory cache
  is best-effort (BR1.5 / NFR5).
* Per-user serialization of the full rehydration critical section is provided by
  a process-level lock in ``SessionService`` (a released row lock cannot span the
  separate re-auth connection). ``SELECT ... FOR UPDATE`` on PostgreSQL is the
  between-instances defense for a future multi-instance topology (BR1.1 /
  NFR5.2); on SQLite the row read is naturally serialized by the connection.
* Expired ``user_session`` rows are lazily deleted on read (Q5-A).
* All SQL is parameterized. No SQL leaks into routers or the god-files (C3).

The repositories accept an injectable ``db`` (defaulting to the shared
``get_db()`` singleton) so tests substitute an in-memory fake instead of Neon.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.services.db_connection import get_db

logger = logging.getLogger(__name__)

# Durable sessions expire 12 hours after last use, matching the legacy
# in-memory TTL so behavior is preserved across the cache/DB boundary.
SESSION_TTL = timedelta(hours=12)


def _utcnow() -> datetime:
    """Return a timezone-aware UTC now (single source of truth for time)."""
    return datetime.now(timezone.utc)


def _as_aware_utc(value) -> Optional[datetime]:
    """Normalize a DB timestamp (str or datetime, naive or aware) to aware UTC.

    Avoids the naive/aware precedence class of bug characterized in
    ``is_refresh_token_valid`` by making the comparison contract explicit.
    """
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass
class SessionRecord:
    """A durable user session as persisted in ``user_session``."""

    user_id: str
    email: str
    futmondo_user_id: str
    last_used: datetime
    created_at: datetime

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or _utcnow()
        last_used = _as_aware_utc(self.last_used) or now
        return now - last_used > SESSION_TTL


@dataclass
class ProtectedCredentialRecord:
    """An encrypted re-auth handle as persisted in ``protected_credential``.

    ``protected_material`` is ciphertext (bytes); the cleartext password is
    never stored. ``scheme`` tags the protection scheme for forward migration.
    """

    user_id: str
    protected_material: bytes
    scheme: str


# --- Idempotent schema (Step 4) ---------------------------------------------


def ensure_durable_session_schema(db=None) -> None:
    """Create the durable-session tables if they do not exist (idempotent).

    Safe to call on every startup: uses ``CREATE TABLE IF NOT EXISTS`` and is a
    no-op when the tables already exist. Called from FastAPI startup so a fresh
    Neon database self-provisions (infra Q1-A).
    """
    db = db or get_db()
    is_pg = db.db_type in ["postgresql", "postgres"]
    material_type = "BYTEA" if is_pg else "BLOB"

    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_session (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                futmondo_user_id TEXT DEFAULT '',
                last_used TIMESTAMP NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
            """
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS protected_credential (
                user_id TEXT PRIMARY KEY,
                protected_material {material_type} NOT NULL,
                scheme TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
            """
        )
    logger.info("Durable-session schema ensured (user_session, protected_credential)")


class SessionRepository:
    """Repository for the durable ``user_session`` table.

    The database is the authority for session existence and freshness; the
    in-memory cache is only a best-effort accelerator.
    """

    def __init__(self, db=None):
        self._db = db or get_db()

    @property
    def _is_pg(self) -> bool:
        return self._db.db_type in ["postgresql", "postgres"]

    def upsert(self, user_id: str, email: str, futmondo_user_id: str = "") -> None:
        """Create or refresh a user's durable session row (idempotent by key).

        Bumps ``last_used`` on every call so an active session stays fresh.
        """
        if not user_id or not email:
            raise ValueError("user_id and email are required to persist a session")

        now = _utcnow()
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            if self._is_pg:
                cursor.execute(
                    """
                    INSERT INTO user_session
                        (user_id, email, futmondo_user_id, last_used, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        email = EXCLUDED.email,
                        futmondo_user_id = EXCLUDED.futmondo_user_id,
                        last_used = EXCLUDED.last_used
                    """,
                    (user_id, email, futmondo_user_id, now, now),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO user_session
                        (user_id, email, futmondo_user_id, last_used, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (user_id) DO UPDATE SET
                        email = excluded.email,
                        futmondo_user_id = excluded.futmondo_user_id,
                        last_used = excluded.last_used
                    """,
                    (user_id, email, futmondo_user_id, now, now),
                )

    def get(self, user_id: str) -> Optional[SessionRecord]:
        """Read a user's durable session, lazily purging it when expired.

        On PostgreSQL the row read uses ``SELECT ... FOR UPDATE``, which holds a
        row lock only for the duration of THIS connection's transaction. Because
        ``get_connection()`` commits and returns the connection to the pool on
        exit, that lock is released when this method returns — it does NOT span
        the subsequent re-auth in ``SessionService`` (which runs on a separate
        connection). Serialization of the full rehydration critical section is
        therefore provided by the per-user process lock in
        ``SessionService.ensure_session`` (see that module's Concurrency note),
        with the database as the cross-instance authority (BR1.5). The
        ``FOR UPDATE`` clause remains a between-instances defense for a future
        topology where the commit envelops the critical section (BR1.1/NFR5.2).
        Expired rows are purged lazily within this same locked read (Q5-A).
        """
        if not user_id:
            return None

        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            if self._is_pg:
                cursor.execute(
                    """
                    SELECT user_id, email, futmondo_user_id, last_used, created_at
                    FROM user_session WHERE user_id = %s FOR UPDATE
                    """,
                    (user_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT user_id, email, futmondo_user_id, last_used, created_at
                    FROM user_session WHERE user_id = ?
                    """,
                    (user_id,),
                )
            row = cursor.fetchone()
            if not row:
                return None

            record = SessionRecord(
                user_id=row[0],
                email=row[1],
                futmondo_user_id=row[2] or "",
                last_used=_as_aware_utc(row[3]),
                created_at=_as_aware_utc(row[4]),
            )

            if record.is_expired():
                # Lazy purge of the expired row within the same locked read.
                self._delete_locked(cursor, user_id)
                return None

            return record

    def touch(self, user_id: str) -> None:
        """Refresh ``last_used`` for an active session without a full upsert."""
        now = _utcnow()
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = "UPDATE user_session SET last_used = ? WHERE user_id = ?"
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (now, user_id))

    def delete(self, user_id: str) -> None:
        """Remove a user's durable session row (on logout)."""
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            self._delete_locked(cursor, user_id)

    def _delete_locked(self, cursor, user_id: str) -> None:
        sql = "DELETE FROM user_session WHERE user_id = ?"
        sql = self._db.adapt_params(sql)
        cursor.execute(sql, (user_id,))


class ProtectedCredentialRepository:
    """Repository for the encrypted re-auth handle (``protected_credential``).

    Only ciphertext crosses this boundary. Callers hand in already-encrypted
    ``protected_material``; this layer never sees or stores cleartext.
    """

    def __init__(self, db=None):
        self._db = db or get_db()

    @property
    def _is_pg(self) -> bool:
        return self._db.db_type in ["postgresql", "postgres"]

    def upsert(self, user_id: str, protected_material: bytes, scheme: str) -> None:
        """Persist (or replace) the encrypted handle for a user (idempotent)."""
        if not user_id:
            raise ValueError("user_id is required to persist a protected credential")
        if not isinstance(protected_material, (bytes, bytearray)):
            raise TypeError("protected_material must be bytes (ciphertext)")

        now = _utcnow()
        material = bytes(protected_material)
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            if self._is_pg:
                cursor.execute(
                    """
                    INSERT INTO protected_credential
                        (user_id, protected_material, scheme, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        protected_material = EXCLUDED.protected_material,
                        scheme = EXCLUDED.scheme,
                        created_at = EXCLUDED.created_at
                    """,
                    (user_id, material, scheme, now),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO protected_credential
                        (user_id, protected_material, scheme, created_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (user_id) DO UPDATE SET
                        protected_material = excluded.protected_material,
                        scheme = excluded.scheme,
                        created_at = excluded.created_at
                    """,
                    (user_id, material, scheme, now),
                )

    def get(self, user_id: str) -> Optional[ProtectedCredentialRecord]:
        """Read the encrypted handle for a user, or ``None`` when absent."""
        if not user_id:
            return None
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = "SELECT user_id, protected_material, scheme FROM protected_credential WHERE user_id = ?"
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            material = row[1]
            if isinstance(material, memoryview):
                material = material.tobytes()
            elif isinstance(material, str):
                # SQLite may return TEXT-affinity blobs as str; encode back.
                material = material.encode("latin-1")
            return ProtectedCredentialRecord(
                user_id=row[0],
                protected_material=bytes(material),
                scheme=row[2],
            )

    def delete(self, user_id: str) -> None:
        """Remove a user's encrypted handle (on logout / hard invalidation)."""
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = "DELETE FROM protected_credential WHERE user_id = ?"
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (user_id,))
