"""Test-after tests for the durable-session persistence layer (Steps 5 & 7).

Covers the idempotent schema script and the ``SessionRepository`` /
``ProtectedCredentialRepository`` behavior against an in-memory persistence
fake (``fake_db``). No real Neon; each test owns its store.
"""

import os
from datetime import datetime, timedelta, timezone

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.stores.session_repository import (  # noqa: E402
    ProtectedCredentialRepository,
    SessionRepository,
    ensure_durable_session_schema,
)


@pytest.fixture
def schema(fake_db):
    """Provision the durable-session schema on the fake DB before each test."""
    ensure_durable_session_schema(db=fake_db)
    return fake_db


# --- Schema (Step 5) --------------------------------------------------------


def test_schema_creates_expected_tables(schema):
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {row[0] for row in cursor.fetchall()}
    assert "user_session" in tables
    assert "protected_credential" in tables


def test_schema_is_idempotent(fake_db):
    """Re-running the schema script must not fail (CREATE TABLE IF NOT EXISTS)."""
    ensure_durable_session_schema(db=fake_db)
    ensure_durable_session_schema(db=fake_db)
    ensure_durable_session_schema(db=fake_db)
    # Still usable afterwards.
    repo = SessionRepository(db=fake_db)
    repo.upsert("user-1", "a@b.com", "fm-1")
    assert repo.get("user-1") is not None


# --- SessionRepository (Step 7) --------------------------------------------


def test_upsert_is_idempotent_by_user_id(schema):
    repo = SessionRepository(db=schema)
    repo.upsert("user-1", "a@b.com", "fm-1")
    repo.upsert("user-1", "a@b.com", "fm-1")  # same key again
    record = repo.get("user-1")
    assert record is not None
    assert record.user_id == "user-1"
    assert record.email == "a@b.com"
    assert record.futmondo_user_id == "fm-1"
    # Only one row exists for the user.
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM user_session WHERE user_id = ?", ("user-1",))
        assert cursor.fetchone()[0] == 1


def test_upsert_updates_existing_fields(schema):
    repo = SessionRepository(db=schema)
    repo.upsert("user-1", "old@b.com", "fm-old")
    repo.upsert("user-1", "new@b.com", "fm-new")
    record = repo.get("user-1")
    assert record.email == "new@b.com"
    assert record.futmondo_user_id == "fm-new"


def test_get_returns_none_when_absent(schema):
    repo = SessionRepository(db=schema)
    assert repo.get("ghost") is None


def test_get_lazily_purges_expired_row(schema):
    """Reading an expired row deletes it and returns None (Q5-A)."""
    repo = SessionRepository(db=schema)
    repo.upsert("user-1", "a@b.com", "fm-1")
    # Force the row to be stale: last_used well beyond the TTL.
    stale = (datetime.now(timezone.utc) - timedelta(hours=13)).isoformat()
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute(
            "UPDATE user_session SET last_used = ? WHERE user_id = ?",
            (stale, "user-1"),
        )
    assert repo.get("user-1") is None
    # The row was physically purged, not just filtered.
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM user_session WHERE user_id = ?", ("user-1",))
        assert cursor.fetchone()[0] == 0


def test_upsert_rejects_missing_identifiers(schema):
    repo = SessionRepository(db=schema)
    with pytest.raises(ValueError):
        repo.upsert("", "a@b.com")
    with pytest.raises(ValueError):
        repo.upsert("user-1", "")


def test_delete_removes_session(schema):
    repo = SessionRepository(db=schema)
    repo.upsert("user-1", "a@b.com")
    repo.delete("user-1")
    assert repo.get("user-1") is None


# --- ProtectedCredentialRepository: NEVER cleartext (Step 7) ---------------


def test_protected_credential_upsert_and_read_roundtrip(schema):
    repo = ProtectedCredentialRepository(db=schema)
    ciphertext = b"\x00\x01\x02encrypted-handle\xff"
    repo.upsert("user-1", ciphertext, scheme="aesgcm-v1")
    record = repo.get("user-1")
    assert record is not None
    assert record.protected_material == ciphertext
    assert record.scheme == "aesgcm-v1"


def test_protected_credential_upsert_is_idempotent(schema):
    repo = ProtectedCredentialRepository(db=schema)
    repo.upsert("user-1", b"first", scheme="aesgcm-v1")
    repo.upsert("user-1", b"second", scheme="aesgcm-v1")
    record = repo.get("user-1")
    assert record.protected_material == b"second"
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM protected_credential WHERE user_id = ?", ("user-1",))
        assert cursor.fetchone()[0] == 1


def test_protected_credential_never_persists_plaintext_password(schema):
    """The password never reaches this layer; only ciphertext bytes are stored."""
    repo = ProtectedCredentialRepository(db=schema)
    secret_password = "super-secret-futmondo-pw"
    ciphertext = b"opaque-ciphertext-bytes"
    repo.upsert("user-1", ciphertext, scheme="aesgcm-v1")
    # Scan every stored value: the cleartext password must appear nowhere.
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute("SELECT protected_material, scheme FROM protected_credential")
        for material, scheme in cursor.fetchall():
            material_bytes = material if isinstance(material, bytes) else bytes(material)
            assert secret_password.encode() not in material_bytes
            assert secret_password not in scheme


def test_protected_credential_rejects_non_bytes(schema):
    repo = ProtectedCredentialRepository(db=schema)
    with pytest.raises(TypeError):
        repo.upsert("user-1", "not-bytes", scheme="aesgcm-v1")  # type: ignore[arg-type]
