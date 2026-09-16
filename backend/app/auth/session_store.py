"""
Per-user Futmondo session cache (best-effort).

Keeps authenticated FutmondoClient instances in memory, keyed by app user_id,
as a cache-aside accelerator in front of the durable session store
(u1-durable-session). The database is the authority for session state and
concurrency (BR1.5 / NFR5); this cache may be cold after a restart, in which
case ``SessionService.ensure_session`` rebuilds the session from the durable
store and the encrypted credential.

Security: this cache NEVER retains the cleartext Futmondo password — not in
memory, not on any attribute (FR5.1 / project.md FORBIDDEN). Re-authentication
after a restart goes through the encrypted credential, not a remembered
password.
"""

import logging
import threading
from datetime import datetime, timedelta
from typing import Optional
from app.services.futmondo_client import FutmondoClient

logger = logging.getLogger(__name__)

# Sessions expire after 12 hours of inactivity
SESSION_TTL = timedelta(hours=12)


class UserSession:
    def __init__(self, client: FutmondoClient, email: str, password: str = ""):
        """Cache entry for a user's live Futmondo client.

        ``password`` is accepted for backward-compatible call sites but is
        intentionally NOT retained (FR5.1): the cleartext credential must never
        live in memory. Re-auth after a cold cache uses the encrypted handle.
        """
        self.client = client
        self.email = email
        self.last_used = datetime.now()
    
    def touch(self):
        self.last_used = datetime.now()
    
    def is_expired(self) -> bool:
        return datetime.now() - self.last_used > SESSION_TTL


class SessionStore:
    """In-memory store for per-user Futmondo sessions."""
    
    def __init__(self):
        self._sessions: dict[str, UserSession] = {}
        self._lock = threading.Lock()
        self._user_locks: dict[str, threading.Lock] = {}
    
    def _get_user_lock(self, user_id: str) -> threading.Lock:
        with self._lock:
            if user_id not in self._user_locks:
                self._user_locks[user_id] = threading.Lock()
            return self._user_locks[user_id]
    
    def get_client(self, user_id: str) -> Optional[FutmondoClient]:
        """Get an authenticated FutmondoClient for a user, or None if not found/expired.

        Best-effort: a miss (cold cache after restart, expiry) returns ``None``
        and the caller rebuilds from the durable store. This method never
        re-creates a session from a remembered password because none is kept.
        """
        user_lock = self._get_user_lock(user_id)
        with user_lock:
            with self._lock:
                session = self._sessions.get(user_id)
            
            if not session:
                return None
            if session.is_expired():
                with self._lock:
                    self._sessions.pop(user_id, None)
                return None
            
            # If the cached client's token went stale we cannot silently
            # re-login (no cleartext password is kept); drop it so the caller
            # rebuilds via the durable credential path.
            if not session.client.is_authenticated():
                with self._lock:
                    self._sessions.pop(user_id, None)
                return None
            
            session.touch()
            return session.client
    
    def create_session(self, user_id: str, email: str, password: str) -> Optional[FutmondoClient]:
        """Create and store a new Futmondo session for a user.

        The password is used transiently to authenticate and is NOT retained in
        the cache entry.
        """
        client = FutmondoClient(email, password)
        if not client.login():
            return None
        
        with self._lock:
            self._sessions[user_id] = UserSession(client, email)
            # Cleanup: remove expired sessions
            expired = [uid for uid, s in self._sessions.items() if s.is_expired()]
            for uid in expired:
                del self._sessions[uid]
        
        logger.info(f"Created Futmondo session for user {user_id}")
        return client
    
    def store_session(self, user_id: str, client: FutmondoClient, email: str, password: str = ""):
        """Store an already-authenticated client (e.g., from login endpoint).

        ``password`` is accepted for backward compatibility with existing call
        sites but is intentionally dropped — never cached (FR5.1).
        """
        with self._lock:
            self._sessions[user_id] = UserSession(client, email)

    def store_reauthenticated(self, user_id: str, client: FutmondoClient, email: str):
        """Cache a client rebuilt by the durable rehydration path (no password)."""
        with self._lock:
            self._sessions[user_id] = UserSession(client, email)
    
    def remove_session(self, user_id: str):
        """Remove a user's session (on logout)."""
        with self._lock:
            self._sessions.pop(user_id, None)


# Global singleton
_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
