"""
Tests del endurecimiento de arranque JWT (NFR1.1).

Cubre los tres casos exigidos por el plan (Step 9) sobre `resolve_jwt_secret`,
más la preservación del worker cron:
1. Secreto AUSENTE en el servicio web -> fallo de arranque (RuntimeError).
2. Secreto igual al DEFAULT inseguro en el web -> fallo de arranque.
3. Secreto válido presente -> arranque correcto (se devuelve el secreto).
Extra: el worker cron arranca sin secreto (nunca emite/valida JWT).

Se prueba la función pura `resolve_jwt_secret` en vez de re-importar el módulo,
porque config.py ya evalúa el guard en tiempo de import; la función pura permite
cubrir los tres casos de forma determinista y aislada.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import pytest  # noqa: E402

from app.core.config import (  # noqa: E402
    JWT_DEFAULT_INSECURE_SECRET,
    is_cron_worker,
    resolve_jwt_secret,
)


def test_web_service_missing_secret_raises():
    with pytest.raises(RuntimeError, match="JWT_SECRET must be set"):
        resolve_jwt_secret("", cron_worker=False)


def test_web_service_default_secret_raises():
    with pytest.raises(RuntimeError, match="must not equal the insecure default"):
        resolve_jwt_secret(JWT_DEFAULT_INSECURE_SECRET, cron_worker=False)


def test_web_service_valid_secret_ok():
    assert resolve_jwt_secret("a-strong-secret", cron_worker=False) == \
        "a-strong-secret"


def test_cron_worker_missing_secret_ok():
    """El worker cron puede arrancar sin secreto (no toca JWT)."""
    assert resolve_jwt_secret("", cron_worker=True) == ""


def test_cron_worker_default_secret_ok():
    """El worker cron no falla aunque el secreto sea el default inseguro."""
    assert resolve_jwt_secret(JWT_DEFAULT_INSECURE_SECRET, cron_worker=True) == \
        JWT_DEFAULT_INSECURE_SECRET


def test_is_cron_worker_detection(monkeypatch):
    """`is_cron_worker` es True solo cuando FLY_APP_NAME contiene 'cron'.

    Independiente de FLY_APP_NAME para el web: sin la variable, se trata como
    servicio web (False)."""
    monkeypatch.setenv("FLY_APP_NAME", "futmondo-cron")
    assert is_cron_worker() is True

    monkeypatch.setenv("FLY_APP_NAME", "futmondo-api")
    assert is_cron_worker() is False

    monkeypatch.delenv("FLY_APP_NAME", raising=False)
    assert is_cron_worker() is False  # sin la var -> web service


def test_web_service_secret_required_independent_of_fly_app_name():
    """Aunque FLY_APP_NAME esté ausente, el web exige secreto (fail-fast)."""
    with pytest.raises(RuntimeError):
        resolve_jwt_secret("", cron_worker=False)
