"""Test estático de verificación TLS (FR8, NFR1.8).

Aserta que:
- El flag huérfano `SSL_VERIFY` ya no aparece en `docker-compose.yml`.
- Ningún cliente HTTP de la ruta de producción (`backend/app/**`) desactiva la
  verificación de certificados con `verify=False` (o equivalente).

Es una aserción estática (lectura de ficheros): no arranca servicios ni hace
red. Las rutas se resuelven de forma robusta relativa a este fichero de test.
"""

import re
from pathlib import Path

# tests/ -> backend/ -> repo root
_TEST_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _TEST_DIR.parent
_REPO_ROOT = _BACKEND_DIR.parent
_APP_DIR = _BACKEND_DIR / "app"
_COMPOSE = _REPO_ROOT / "docker-compose.yml"

# Match `verify=False` allowing arbitrary whitespace around `=` (e.g. requests /
# curl_cffi / httpx style client calls). Case-insensitive on the boolean.
_VERIFY_FALSE = re.compile(r"verify\s*=\s*False", re.IGNORECASE)


def test_ssl_verify_flag_absent_from_docker_compose():
    assert _COMPOSE.exists(), f"docker-compose.yml not found at {_COMPOSE}"
    content = _COMPOSE.read_text(encoding="utf-8")
    assert "SSL_VERIFY" not in content, (
        "El flag huérfano 'SSL_VERIFY' no debe reaparecer en docker-compose.yml"
    )


def test_no_verify_false_in_production_http_clients():
    offenders = []
    for py_file in _APP_DIR.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        for match in _VERIFY_FALSE.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            rel = py_file.relative_to(_REPO_ROOT)
            offenders.append(f"{rel}:{line_no}")
    assert not offenders, (
        f"Clientes HTTP de producción con verificación TLS desactivada (verify=False): {offenders}"
    )
