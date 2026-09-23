# Diseño de dominio — Componentes

> Conversation language: Spanish. Lead: aidlc-architect-agent. Consume
> `requirements.md` y el codekb (`architecture`, `component-inventory`).
> Backend-only, coste 0 €, sin ampliar god-files. Cambios aditivos.

## Contexto verificado (código real, `main` 2026-09-21)

- El **estado por-paso** de la sync vive en `task.progress[step]`, un dict JSON
  libre con forma `{"status": "running" | "done", ...}` (`task_manager.py`
  `update_progress`; `TaskRecord.progress` en `task_service.py` es el mismo dict,
  persistido). El `status` de la **tarea** (pending/running/completed/failed/
  interrupted_by_restart) es distinto y NO se toca.
- El bug de FR3.1 (`sync.py:143-164`): el `except` de `prizes`/`phantoms` escribe
  `progress[step] = {"status": "done", ..., "error": str(err)}` — marca el paso
  como `done` pese al fallo.
- `market.py::place_bid` valida `price <= 0` → 422; no hay techo superior.

## Componentes del diseño

### C1 — Valor de estado de paso `DEGRADED` (aditivo)

- Introducir la constante `StepStatus.DEGRADED = "degraded"` (nuevo módulo estrecho
  `step_status.py` o constante junto a `TaskStatus`), como valor válido del campo
  `status` **dentro** de `progress[step]`. No es un estado de la Tarea; es del paso.
- Aditivo: no cambia el esquema (`progress` ya es JSON libre en memoria y en la BD
  durable). Un paso OK sigue con `"done"`.

### C2 — Helper `record_degraded_step` (función estrecha testeable)

- Firma: `record_degraded_step(tm, task_id, step, reason, extra=None)`.
- Efecto: `tm.update_progress(task_id, step, {"status": DEGRADED, "reason": reason, **(extra or {})})`
  + **log estructurado** (`logger.warning`/`error` con campos `step`, `reason`).
- Vive **fuera** del god-file (`data_sync_service.py`), en un módulo estrecho del
  paquete de servicios de sync. Reutilizable por otros pasos en el futuro.
- Contrato tipado del payload de paso degradado (R-02): `{status: "degraded", reason: str, [extra]}`.

### C3 — Cableado de `prizes` y `phantoms` (`sync.py`)

- En las ramas `except` de `prizes` y `phantoms` (`sync.py:148-164`), sustituir
  el `update_progress(..., {"status": "done", ..., "error": ...})` por una llamada
  a `record_degraded_step(...)`. El resto del bucle no cambia.

### C4 — Política de `except` acotada (FR3.2)

- En arranque/migraciones (`db_connection.py`, `auth/token_store.py` y
  equivalentes en alcance) + los `except` del camino de sync tocado por C3:
  distinguir **recuperable** (log estructurado + continuar/reintentar) de **fatal**
  (propagar con contexto). Sin capturar-y-silenciar.
- Clasificación por locus (R-02) se detalla en functional-design; principio aquí.

### C5 — Techo de sanidad de `price` (`market.py::place_bid`)

- Añadir, junto a la validación `price <= 0` existente, un **techo**:
  `if price > PRICE_SANITY_CAP: raise HTTPException(422, ...)`.
- `PRICE_SANITY_CAP` es una constante documentada (R-03): múltiplo holgado del
  presupuesto máximo plausible (valor exacto en functional-design). Sin red.

## Diagrama (texto)

```
sync.py (bucle de 11 pasos)
  └─ prizes/phantoms except ──► record_degraded_step(tm, task_id, step, reason)   [C2/C3]
                                    ├─ update_progress → progress[step].status = "degraded"  [C1]
                                    └─ log estructurado (step, reason)
task_manager.Task.progress[step] = {status, reason, ...}   (in-memory)     [C1]
task_service.TaskRecord.progress                            (durable, mismo dict) [C1]

market.py::place_bid
  ├─ price <= 0 → 422           (ya existe)
  └─ price > PRICE_SANITY_CAP → 422   [C5]

arranque/migraciones + except del sync ──► recuperable(log+continuar) | fatal(propagar)  [C4]
```

## Sources

- Consume `inception/requirements-analysis/requirements.md` (FR3.1/FR3.2/FR6, NFR).
- Código verificado: `task_manager.py`, `task_service.py`, `sync.py:143-164`, `market.py:122-186`.
- Hallazgos R-01/R-02/R-03 de la revisión de requisitos.

## Assumptions & Open Questions

- [assumption] `progress` como JSON libre admite el nuevo valor `degraded` sin migración de BD (confirmado por lectura de `task_service.py`/`TaskRecord`).
- Valor exacto de `PRICE_SANITY_CAP` y la tabla recuperable/fatal por locus: functional-design.
