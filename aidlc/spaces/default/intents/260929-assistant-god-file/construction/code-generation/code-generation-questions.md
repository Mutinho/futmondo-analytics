# Code Generation — Questions

## Plan Approval

Aprobación del plan de generación de código para la descomposición DDD de `assistant_service.py`.
Cubre `code-generation-plan.md` (con su Testing Contract embebido) y `unit-test-instructions.md`.

Notas del revisor de arquitectura (READY) a honrar durante la generación (guía de implementación,
no cambian el plan a nivel arquitectónico):
- R-01: la ruta real de las fixtures es `backend/conftest.py` (no `backend/tests/conftest.py`); el
  developer debe importar/usar `fake_db` desde su ubicación real.
- R-03: la degradación de las lecturas de contexto NO es uniforme — congelar el comportamiento
  observable POR RAMA (p. ej. `_ctx_market_from_db` degrada con `except Exception: return ""`, otras
  `_ctx_*` pueden no hacerlo); caracterizar cada rama como está.
- R-04: hay un segundo `CREATE TABLE IF NOT EXISTS market_today` en caliente dentro de
  `_save_market_to_db`; ese DDL también va al adaptador de infraestructura (FR4.1/FR4.2).
- R-02: aseverar en los tests que una respuesta factual NO invoca `can_make_request`/`record_usage`
  (cortocircuita antes de la cuota), congelando el orden observable real.

[Approval Fingerprint]: sha256:v3:a6d162291b47758c3fc779931fc63605ed9b2eeeeadee4e61feb6872aad66b2c
[Planned Source]: 9fadefd39955416831e2c27a61cfcffa86d8de4c935ced3740febcad7f1cb914

- Approve Plan — proceed to code generation
- Request Changes — revise the plan

[Answer]: Approve Plan
