"""Durable session orchestration (u1-durable-session).

``SessionService.ensure_session`` is the idempotent entry point (BR1.2) that
guarantees an authenticated Futmondo client for a user, rebuilding it after a
restart when the in-memory cache is cold:

    cache (SessionStore) -> DB (SessionRepository) -> rehydrate (CredentialProtection)

Failure taxonomy (BR1.3, Q4-A):

* **Transient** (network/upstream hiccup during re-auth): surfaced as
  ``TransientSessionError``. The stored handle is NOT destroyed and the user is
  NOT logged out; the caller may retry later.
* **Unrecoverable** (no durable session AND no usable credential, or the
  credential is rejected/undecryptable): surfaced as
  ``SessionUnrecoverableError``. The API layer maps this to an actionable 401.

No internal retries (BR1.6): a single pass per call. Errors are typed
exceptions; there is never a silent ``except: pass``.

Concurrency (BR1.1 / BR1.2 / NFR5.2): rehydration of a single ``user_id`` is
serialized *within this process* by a per-user lock (see ``_UserLocks``). Two
concurrent ``ensure_session(user_id)`` calls for the same user therefore never
trigger two re-authentications — the first rebuilds and warms the cache, and the
second, entering the critical section afterwards, observes the warm cache and
reuses that result (idempotency). This intra-process serialization is sufficient
for the current deployment (``min=max=1`` Fly.io machine); the database remains
the authority for cross-instance state (BR1.5), and ``SELECT ... FOR UPDATE`` in
the repository is the between-instances defense for a future multi-instance
topology where the commit envelops the critical section. It deliberately does
NOT assume a single instance incorrectly: correctness across instances still
rests on the DB, this lock only removes the intra-process race.

``ensure_session`` uses ``camelCase`` alias ``ensureSession`` to match the
contract-summary interface name while the Python-idiomatic ``ensure_session``
is the primary spelling.
"""

import logging
import threading
from typing import Optional

import requests

from app.security.credential_protection import (
    CredentialProtection,
    CredentialProtectionUnavailable,
    FutmondoSession,
)
from app.services.futmondo_client import FutmondoClient

logger = logging.getLogger(__name__)


class SessionError(Exception):
    """Base class for durable-session domain errors."""


class TransientSessionError(SessionError):
    """A recoverable, retryable failure (network/upstream). Do NOT log out."""


class SessionUnrecoverableError(SessionError):
    """No usable session and no way to rebuild one. Requires a fresh login."""


class _UserLocks:
    """Registry of per-user re-entrant-free locks for intra-process serialization.

    Hands out one ``threading.Lock`` per ``user_id`` so that concurrent
    rehydrations of the SAME user serialize, while different users proceed in
    parallel. The registry itself is guarded by a short-lived meta-lock; the
    per-user locks are never held while acquiring the meta-lock, so there is no
    lock-ordering inversion. Locks are retained for the process lifetime (one
    tiny ``Lock`` per distinct user id — bounded by the active user base and
    cheap; no unbounded growth concern at this scale).
    """

    def __init__(self):
        self._meta = threading.Lock()
        self._locks: dict[str, threading.Lock] = {}

    def get(self, user_id: str) -> threading.Lock:
        with self._meta:
            lock = self._locks.get(user_id)
            if lock is None:
                lock = threading.Lock()
                self._locks[user_id] = lock
            return lock


class SessionService:
    """Coordinates the cache, durable store, and credential rehydration."""

    def __init__(self, session_store, session_repository, credential_protection=None):
        self._cache = session_store
        self._repository = session_repository
        self._protection = credential_protection
        # Per-user serialization of the cache->DB->rehydrate critical section.
        self._user_locks = _UserLocks()

    def ensure_session(self, user_id: str) -> FutmondoClient:
        """Return an authenticated client for ``user_id``, rebuilding if needed.

        Idempotent: repeated calls converge on the same live session without
        creating duplicates. Concurrent calls for the same ``user_id`` are
        serialized by a per-user lock so at most ONE re-authentication happens;
        the loser of the race reuses the winner's warmed cache (BR1.1/BR1.2).
        Raises ``TransientSessionError`` on a recoverable failure and
        ``SessionUnrecoverableError`` when a fresh login is required.
        """
        if not user_id:
            raise SessionUnrecoverableError("Missing user identity for session resolution")

        # Fast path: a warm cache needs no lock (best-effort accelerator, BR1.5).
        cached = self._cache.get_client(user_id)
        if cached is not None:
            return cached

        # Serialize the rehydration critical section for this user so two
        # concurrent cold-cache callers do not both re-authenticate.
        with self._user_locks.get(user_id):
            # Re-check inside the lock: the winner of the race may have just
            # warmed the cache while we were blocked (idempotency, BR1.2).
            cached = self._cache.get_client(user_id)
            if cached is not None:
                return cached

            # Durable store: a session row means the user had a valid session; we
            # still need a live client, so a row alone is not enough — we must
            # rehydrate from the protected credential. The row informs whether the
            # durable session existed (for touch/telemetry); rehydration is the
            # authority for producing a live client.
            session_record = self._repository.get(user_id)

            # Rehydrate via the protected credential.
            rebuilt = self._rehydrate(user_id)
            if rebuilt is None:
                raise SessionUnrecoverableError("No recoverable Futmondo credential for this user")

            # Repopulate the cache and refresh the durable row (idempotent upsert).
            self._cache.store_reauthenticated(user_id, rebuilt.client, rebuilt.email)
            self._repository.upsert(user_id, rebuilt.email, rebuilt.futmondo_user_id)
            if session_record is not None:
                # Keep last_used fresh for an already-known durable session.
                self._repository.touch(user_id)
            return rebuilt.client

    # camelCase alias to match the contract-summary interface name (BR1.2).
    ensureSession = ensure_session

    def _rehydrate(self, user_id: str) -> Optional[FutmondoSession]:
        """Attempt to rebuild the session from the encrypted handle.

        Returns the rebuilt session, or ``None`` when unrecoverable. Raises
        ``TransientSessionError`` on a network/upstream failure so the caller
        does not tear down a still-valid handle.
        """
        if self._protection is None:
            # Protection layer not wired (e.g. key unset): cannot rebuild.
            return None
        try:
            return self._protection.reauthenticate(user_id)
        except CredentialProtectionUnavailable:
            # Misconfiguration, not a per-user credential problem. Treated as
            # unrecoverable for this request rather than a silent pass.
            logger.error("Credential protection unavailable while rehydrating session")
            return None
        except (requests.exceptions.RequestException, TimeoutError) as exc:
            # Network/upstream hiccup: recoverable. Preserve the handle.
            raise TransientSessionError(
                "Transient failure while re-authenticating Futmondo session"
            ) from exc


# --- Provider ---------------------------------------------------------------

_service: Optional["SessionService"] = None


def get_session_service() -> "SessionService":
    """Return a process-wide ``SessionService`` wired to the live dependencies.

    Wires the singleton in-memory cache, a durable ``SessionRepository``, and
    (when ``FUTMONDO_CRED_KEY`` is configured) the ``CredentialProtection``
    layer. When the key is absent the service still runs; rehydration then
    yields an unrecoverable result (a fresh login is required) rather than
    crashing unrelated endpoints.
    """
    global _service
    if _service is None:
        from app.auth.session_store import get_session_store
        from app.stores.session_repository import (
            ProtectedCredentialRepository,
            SessionRepository,
        )

        protection = None
        try:
            protection = CredentialProtection(ProtectedCredentialRepository())
        except CredentialProtectionUnavailable:
            logger.warning(
                "FUTMONDO_CRED_KEY not configured; durable rehydration disabled "
                "(sessions lost on restart will require a fresh login)"
            )

        _service = SessionService(
            session_store=get_session_store(),
            session_repository=SessionRepository(),
            credential_protection=protection,
        )
    return _service
