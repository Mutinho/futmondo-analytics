"""Credential protection for durable Futmondo sessions (u1-durable-session).

Encrypts the Futmondo re-auth handle at rest so a session can be rebuilt after a
restart WITHOUT ever persisting the password in cleartext (FR5.1 / NFR1 /
BR1.4). The re-auth handle for Futmondo is the ``(email, password)`` pair,
because ``FutmondoClient.login()`` needs both to obtain a fresh token; we never
store that pair in cleartext, only its AES-GCM (Fernet) ciphertext.

DEVIATION FROM THE APPROVED ADR — surfaced for the human gate, NOT silenced
=========================================================================
The approved security-design ADR prescribed persisting a reusable *re-auth
handle* (a Futmondo token/refresh token derived from login) and REJECTED
"encrypt the password" as the alternative (a master key without TTL). That ADR
is INFEASIBLE against the real Futmondo API at 0€, verified objectively:

* ``FutmondoClient`` (``app/services/futmondo_client.py``) is constructed as
  ``FutmondoClient(email, password)`` and only becomes authenticated via
  ``login()``, which POSTs ``{"query": {"mail", "pwd"}}`` to ``/5/login/with_mail``
  with a hardcoded ``header.token = "null"`` (i.e. login ALWAYS requires the
  password; there is no refresh flow).
* ``login()`` captures ``self.token`` / ``self.user_id`` from the response, but
  there is NO method to reconstruct a working client from a token alone — no
  ``set_token`` / ``from_token`` / refresh endpoint. Authenticated requests use
  ``self.session`` (cookies established during ``login``) plus ``self.token``;
  the token is not independently persistable into a rebuilt client.

Therefore the ADR's reusable-token handle cannot be built, and the ONLY 0€ way
to satisfy FR1.2 (transparent re-auth after restart) is to encrypt the
``(email, password)`` credential at rest. This still honors the hard rule
(never cleartext at rest, FR5.1/BR1.4) and FR5.2 ("encrypted at rest with a
key managed as a secret"), but it is the alternative the ADR rejected, so the
orchestrator MUST raise this to the human at the gate to decide whether to
accept the deviation or revisit the design. The ``scheme`` tag names this
honestly (``encrypted-credential+fernet-v1``) rather than pretending a token
handle is stored.

Security invariants enforced here:

* ``protect`` derives the handle, encrypts it with the key from
  ``FUTMONDO_CRED_KEY``, and NEVER retains the plaintext — it lives in an
  ephemeral local variable, never an attribute, never a log line.
* The decrypted handle NEVER crosses the public boundary: ``reauthenticate``
  decrypts in memory, re-authenticates internally, and returns only the rebuilt
  session (or ``None``). ``resolve`` (the decrypt step) is private.
* ``ReauthMaterial`` uses ``__slots__`` and redacts ``__repr__`` / ``__str__`` so
  the handle cannot leak into logs or tracebacks (deterministic anti-log
  control).
"""

import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import FUTMONDO_CRED_KEY
from app.services.futmondo_client import FutmondoClient

logger = logging.getLogger(__name__)

# Protection scheme tag persisted alongside the ciphertext for forward
# migration. Fernet is AES-128-CBC + HMAC authenticated encryption. The name is
# honest about WHAT is encrypted: the (email, password) credential pair, because
# the Futmondo API exposes no reusable token handle to persist instead (see the
# module docstring's DEVIATION note). Rotating the scheme (``-v2``) allows
# re-encryption without a hard migration.
SCHEME_ENCRYPTED_CREDENTIAL_V1 = "encrypted-credential+fernet-v1"

# Field separator inside the plaintext handle. Email addresses cannot contain a
# newline, so this unambiguously splits the two fields after decryption.
_HANDLE_SEPARATOR = "\n"


class CredentialProtectionUnavailable(RuntimeError):
    """Raised at construction when no protection key is configured.

    Distinct from a transient runtime failure: this means the deployment is
    missing ``FUTMONDO_CRED_KEY`` and credential protection cannot operate at
    all. Callers treat it as a configuration error, not a per-user failure.
    """


class ReauthMaterial:
    """In-memory, redacted holder for a decrypted re-auth handle.

    Never logged, never serialized. ``__repr__`` and ``__str__`` are redacted so
    an accidental ``log.info(material)`` or a traceback frame cannot leak the
    credential. Instances are short-lived and confined to ``reauthenticate``.
    """

    __slots__ = ("_email", "_password")

    def __init__(self, email: str, password: str):
        self._email = email
        self._password = password

    @property
    def email(self) -> str:
        return self._email

    @property
    def password(self) -> str:
        return self._password

    def __repr__(self) -> str:  # noqa: D401 - redacted on purpose
        return "<ReauthMaterial redacted>"

    def __str__(self) -> str:
        return "<ReauthMaterial redacted>"


class FutmondoSession:
    """A rebuilt Futmondo session handed back across the protection boundary.

    Carries only the authenticated client and non-secret identity fields. The
    re-auth handle is NOT part of this object — it never leaves
    ``CredentialProtection``.
    """

    __slots__ = ("client", "email", "futmondo_user_id")

    def __init__(self, client: FutmondoClient, email: str, futmondo_user_id: str):
        self.client = client
        self.email = email
        self.futmondo_user_id = futmondo_user_id


class CredentialProtection:
    """Encrypts, stores, and rebuilds Futmondo re-auth handles.

    Depends on a ``ProtectedCredentialRepository`` (the persistence boundary) and
    the ``FUTMONDO_CRED_KEY`` symmetric key. The repository only ever sees
    ciphertext.
    """

    def __init__(self, repository, key: Optional[str] = None):
        self._repository = repository
        raw_key = key if key is not None else FUTMONDO_CRED_KEY
        if not raw_key:
            raise CredentialProtectionUnavailable(
                "FUTMONDO_CRED_KEY is not configured; credential protection "
                "cannot encrypt or decrypt re-auth handles."
            )
        # Fernet keys are 32 url-safe base64 bytes. Accept the key as provided;
        # a malformed key fails loudly here rather than silently degrading.
        self._fernet = Fernet(raw_key if isinstance(raw_key, bytes) else raw_key.encode())

    def protect(self, user_id: str, email: str, plaintext_password: str) -> None:
        """Encrypt and persist the re-auth handle for ``user_id``.

        The plaintext password lives ONLY in the ephemeral ``handle`` local
        below; it is never stored on ``self``, never logged, and never returned.
        """
        if not user_id or not email or not plaintext_password:
            raise ValueError("user_id, email and password are required to protect a credential")

        # Ephemeral local: encrypted immediately, never retained.
        handle = f"{email}{_HANDLE_SEPARATOR}{plaintext_password}"
        ciphertext = self._fernet.encrypt(handle.encode("utf-8"))
        self._repository.upsert(user_id, ciphertext, scheme=SCHEME_ENCRYPTED_CREDENTIAL_V1)

    def can_reauthenticate(self, user_id: str) -> bool:
        """True when an encrypted handle exists for ``user_id`` (no decrypt)."""
        return self._repository.get(user_id) is not None

    def forget(self, user_id: str) -> None:
        """Delete the stored encrypted handle for ``user_id`` (on logout)."""
        self._repository.delete(user_id)

    def reauthenticate(self, user_id: str) -> Optional[FutmondoSession]:
        """Rebuild a Futmondo session for ``user_id`` from the stored handle.

        Decrypts in memory, re-authenticates internally, and returns the rebuilt
        session, or ``None`` when the credential is missing/undecryptable or the
        upstream login rejects it (unrecoverable). Transient/network failures are
        surfaced as exceptions by ``FutmondoClient`` and propagate to the caller,
        which decides not to destroy the handle (BR1.3). The decrypted handle is
        confined to this method and never crosses the return boundary.
        """
        material = self._resolve(user_id)
        if material is None:
            return None

        client = FutmondoClient(material.email, material.password)
        # ``login`` returns False on invalid credentials and only raises on a
        # transient transport failure it cannot classify; we let those propagate
        # so the service layer can distinguish transient from unrecoverable.
        if not client.login():
            return None

        return FutmondoSession(
            client=client,
            email=material.email,
            futmondo_user_id=client.user_id or "",
        )

    def _resolve(self, user_id: str) -> Optional[ReauthMaterial]:
        """PRIVATE: decrypt the stored handle into redacted in-memory material.

        Returns ``None`` when there is no stored handle or the ciphertext cannot
        be decrypted (tampered / wrong key) — both are unrecoverable, not
        transient.
        """
        record = self._repository.get(user_id)
        if record is None:
            return None
        try:
            plaintext = self._fernet.decrypt(record.protected_material).decode("utf-8")
        except (InvalidToken, ValueError):
            logger.warning(
                "Could not decrypt stored credential for a user; treating as unrecoverable"
            )
            return None
        email, _, password = plaintext.partition(_HANDLE_SEPARATOR)
        return ReauthMaterial(email=email, password=password)
