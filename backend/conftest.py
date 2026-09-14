"""
Fixtures compartidas para la suite de caracterización (red de seguridad).

Estos tests congelan el comportamiento ACTUAL del código existente antes de
refactorizarlo (metodología `custom`, characterization-first — ver Testing
Contract del plan). No usan BD real: se inyectan fakes de `DataManager`/conexión
por fixture (patrón de `test_analytics_service.py`) y factories/fakes para las
APIs externas. Nunca se copian datos ni credenciales reales a los tests.
"""

import os
import sys

import pytest

# Asegura que `from app...` resuelve al ejecutar desde backend/ (R-01). pytest.ini
# ya fija pythonpath = . ; esto lo hace robusto si se invoca de otra forma.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


@pytest.fixture
def clean_jwt_env(monkeypatch):
    """Aísla las variables de entorno que gobiernan el arranque JWT/servicio.

    Cada test que ejercita `app.core.config` debe partir de un entorno conocido
    para no depender del `.env` de la máquina de desarrollo.
    """
    for var in ("JWT_SECRET", "FLY_APP_NAME"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch
