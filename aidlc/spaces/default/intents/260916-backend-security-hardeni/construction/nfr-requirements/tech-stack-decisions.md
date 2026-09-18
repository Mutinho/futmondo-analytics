# Decisiones de Stack Tecnológico — Backend Security Hardening

> Scope `security-patch`, depth Minimal. Proyecto brownfield: el stack está fijado.

## Decisión: mantener el stack actual sin cambios

- **NFR-TECH.1**: No se introduce ninguna tecnología nueva. Las cinco correcciones se implementan con el stack existente. Restricción del intent: mantener Angular + FastAPI + Neon PostgreSQL + Fly.io, sin reescrituras grandes. `[memory:technology-stack.md]`

| Capa | Tecnología (sin cambios) | Uso en este intent |
|---|---|---|
| Validación de entrada (FR6) | `pydantic` / `Query` de FastAPI ya presentes | Validar `price > 0` en el endpoint, 422 idiomático |
| Auth / refresh (FR9) | `PyJWT==2.9.0`, `psycopg2-binary`, `datetime` stdlib | Corregir precedencia naive/aware con `datetime` correcto |
| Cliente HTTP / TLS (FR8) | `requests`, `curl_cffi` ya presentes | Garantizar verificación TLS activa; eliminar flag huérfano |
| Endpoints admin (FR18) | FastAPI + guard `_require_db_admin` existente | Confirmar guarda + test |
| Test | `pytest>=8.0.0`, `pytest-cov`, `httpx` (`TestClient`) | Tests de regresión por FR con fakes de `conftest.py` |

## Justificación

- **Coste 0 €** (regla `## Mandated`): ninguna dependencia nueva de pago; se usan librerías ya en `requirements.txt`. `[memory:project.md]`
- **Sin ampliar deuda** (regla `## Code Style`): la validación y correcciones van tras capas estrechas / en el boundary, sin ampliar SQL-en-router ni los god-files (`data_manager_v2.py`, `data_sync_service.py`). `[memory:team.md]`
- **Idioma en el código**: identificadores/docstrings en inglés; `HTTPException.detail` en castellano. `[memory:team.md]`

## Assumptions & Open Questions

None.

<!-- Re-anclado 2026-09-17 (redo-jump; contenido sin cambios). -->

<!-- Re-guardado 2026-09-17 tras confirmación vigente (contenido sin cambios). -->
