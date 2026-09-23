# Especificación funcional — U1 sync-reliability

> Conversation language: Spanish. Unidad: sync-reliability. Consume contratos
> (CT1-CT4), diseño de dominio (C1-C5, ADR-1..4) y requisitos. Backend-only,
> aditivo, sin ampliar god-files, coste 0 €. Resuelve R-01/R-02/R-03.

## Ubicación del código (R-02)

- Nuevo módulo estrecho `backend/app/services/sync_step_status.py`:
  - `StepStatus` con `RUNNING = "running"`, `DONE = "done"`, `DEGRADED = "degraded"`.
  - `record_degraded_step(tm, task_id, step, reason, extra=None)`.
- Modificaciones acotadas: `backend/app/api/v1/endpoints/sync.py` (cableado),
  `backend/app/api/v1/endpoints/market.py` (techo), y los `except` de arranque/
  migraciones en alcance.

## FS1 — Helper `record_degraded_step` (CT1, C2; R-01)

```python
# backend/app/services/sync_step_status.py
import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class StepStatus:
    RUNNING = "running"
    DONE = "done"
    DEGRADED = "degraded"


class ProgressSink(Protocol):
    """Común a TaskManager (in-memory) y TaskService (durable)."""
    def update_progress(self, task_id: str, step: str, data: dict) -> None: ...


def record_degraded_step(
    tm: ProgressSink,
    task_id: str,
    step: str,
    reason: str,
    extra: dict | None = None,
) -> None:
    """Marca un paso non-critical como degradado y emite un log estructurado.

    No propaga: es el manejador de un fallo ya capturado.
    """
    payload = {"status": StepStatus.DEGRADED, "reason": reason}
    if extra:
        payload.update(extra)
    tm.update_progress(task_id, step, payload)
    logger.warning("sync step degraded", extra={"sync_step": step, "reason": reason})
```

- R-01 resuelto: el parámetro se tipa con un `Protocol` (`ProgressSink`) que cubre
  tanto `TaskManager` como `TaskService` (el objeto real cableado en `sync.py:87`
  es `TaskService`). Ambos exponen `update_progress(task_id, step, data)`.
- R-02 resuelto: `StepStatus` vive en este módulo; la validez de `degraded` es por
  convención + tests (no hay esquema que lo imponga; `progress` es JSON libre).

## FS2 — Cableado de `prizes`/`phantoms` (CT-C3, `sync.py:143-164`)

Reemplazar las ramas `except` que hoy escriben `{"status": "done", ..., "error": ...}`:

```python
# --- Prizes ---
tm.update_progress(task_id, "prizes", {"status": "running"})
try:
    prizes_result = sync_service.sync_prizes()
    tm.update_progress(task_id, "prizes", {"status": "done", **prizes_result})
    results["prizes"] = prizes_result
except Exception as pr_err:
    record_degraded_step(tm, task_id, "prizes", str(pr_err), {"records_synced": 0})
    results["prizes"] = {"records_synced": 0}

# --- Check phantoms ---
tm.update_progress(task_id, "phantoms", {"status": "running"})
try:
    phantoms_result = _check_phantoms(championship_id, client, user_id)
    tm.update_progress(task_id, "phantoms", {"status": "done", **phantoms_result})
    results["phantoms"] = phantoms_result
except Exception as ph_err:
    record_degraded_step(tm, task_id, "phantoms", str(ph_err), {"total_phantoms": 0})
    results["phantoms"] = {"total_phantoms": 0}
```

- El paso queda con `status == "degraded"` (no `done`); el consumidor de NFR1 lee
  `progress[step].status` (R-03 del review de dominio ya cubierto por el contrato).

## FS3 — Techo de `price` (CT3, C5; R-03)

```python
# backend/app/api/v1/endpoints/market.py (constante a nivel de módulo)
# Techo de sanidad: múltiplo holgado del presupuesto máximo plausible de un
# campeonato Futmondo. No es el límite real del mercado (ese lo valida Futmondo);
# es una barrera contra overflow/abuso de un entero descontrolado.
PRICE_SANITY_CAP = 5_000_000_000  # 5.000 M€, ~10x un presupuesto alto plausible

# dentro de place_bid, junto al price <= 0 existente:
if price <= 0:
    raise HTTPException(status_code=422, detail="El precio de la puja debe ser un entero positivo")
if price > PRICE_SANITY_CAP:
    raise HTTPException(status_code=422, detail="El precio de la puja excede el límite permitido")
```

- R-03 resuelto: valor fijo documentado y justificado; el test aseverará este
  umbral estable. Sin llamada de red.

## FS4 — `except` acotados (CT4, C4; R-02 tabla recuperable/fatal)

Tabla por locus en alcance (loci verificados contra `main` 2026-09-21):

| Locus | Fallo | Clasificación | Acción |
|---|---|---|---|
| `db_connection.py:134-140` creación del pool PostgreSQL | pool no creable | Recuperable (ya tratado) | Ya hace log + fallback a conexiones directas; se conserva |
| `db_connection.py:183-188` reintento de conexión del pool (conn muerta) | conexión del pool muerta | Recuperable | Descartar y reintentar; el `except Exception: pass` de `:187-188` (putconn de una conn ya muerta) recibe un log de contexto en vez de silencio |
| `token_store.py:108-109` `init_auth_tables` (`except Exception: pass  # Column already exists`) | columna/objeto ya existe (migración idempotente) | Recuperable | Estrechar a la excepción esperada de "ya existe" + log a debug; no tragar cualquier `Exception` |
| `sync.py` pasos `prizes`/`phantoms` | excepción del paso | Recuperable (degradado) | `record_degraded_step` (FS2) |

- Prohibido `except Exception: pass` mudo en estos loci; todo recuperable deja log,
  y el de `init_auth_tables` se estrecha a la excepción de "ya existe" (hoy captura
  cualquier `Exception`, lo que enmascararía un fallo real de migración).
- No hay un locus de "limpieza de tokens expirados" por `except` (la expiración se
  resuelve por query en `is_refresh_token_valid`), corrección del anclaje previo.

## Sources

- Consume `inception/contract-design/contract-summary.md` (CT1-CT4), `inception/domain-design/*`, `inception/requirements-analysis/requirements.md`.
- Código verificado: `sync.py:80-164` (tm = get_task_service()), `market.py::place_bid`, `db_connection.py`, `auth/token_store.py`.

## Assumptions & Open Questions

None.
