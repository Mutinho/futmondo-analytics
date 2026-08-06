"""
Per-user Futmondo session store.
Keeps authenticated FutmondoClient instances in memory, keyed by app user_id.
Sessions expire after inactivity and are re-created on next request if needed.
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
    def __init__(self, client: FutmondoClient, email: str, password: str):
        self.client = client
        self.email = email
        self.password = password
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
        """Get an authenticated FutmondoClient for a user, or None if not found/expired."""
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
            
            # Re-authenticate if token might be stale
            if not session.client.is_authenticated():
                logger.info(f"Re-authenticating Futmondo session for user {user_id}")
                if not session.client.login():
                    with self._lock:
                        self._sessions.pop(user_id, None)
                    return None
            
            session.touch()
            return session.client
    
    def create_session(self, user_id: str, email: str, password: str) -> Optional[FutmondoClient]:
        """Create and store a new Futmondo session for a user."""
        client = FutmondoClient(email, password)
        if not client.login():
            return None
        
        with self._lock:
            self._sessions[user_id] = UserSession(client, email, password)
            # Cleanup: remove expired sessions
            expired = [uid for uid, s in self._sessions.items() if s.is_expired()]
            for uid in expired:
                del self._sessions[uid]
        
        logger.info(f"Created Futmondo session for user {user_id}")
        return client
    
    def store_session(self, user_id: str, client: FutmondoClient, email: str, password: str):
        """Store an already-authenticated client (e.g., from login endpoint)."""
        with self._lock:
            self._sessions[user_id] = UserSession(client, email, password)
    
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
