# Diseño de contratos — Fiabilidad de la sync

> Conversation language: Spanish. Lead: aidlc-architect-agent. Consume el diseño
> de dominio (C1-C5, ADR-1..4) y los requisitos. Backend-only, coste 0 €.

## Contratos

### CT1 — Helper `record_degraded_step` (interfaz interna)

```python
def record_degraded_step(
    tm: TaskManager,
    task_id: str,
    step: str,
    reason: str,
    extra: dict | None = None,
) -> None:
    """Marca un paso non-critical como degradado en el estado de la tarea y
    emite un log estructurado. Escribe progress[step] con status="degraded"."""
```

- Efecto: `tm.update_progress(task_id, step, {"status": "degraded", "reason": reason, **(extra or {})})`
  + `logger.warning`/`error` con campos estructurados `step`, `reason`.
- No lanza: es el manejador de un fallo ya capturado; su trabajo es registrar, no propagar.

### CT2 — Contrato del payload de paso degradado (R-02)

Forma canónica de `progress[step]` para un paso degradado:

```json
{ "status": "degraded", "reason": "<motivo legible>", "...": "campos extra opcionales" }
```

- `status`: uno de `"running" | "done" | "degraded"` (valor `degraded` es el nuevo).
- Válido tanto en el `TaskManager` in-memory como en `TaskRecord.progress` durable
  (mismo dict JSON libre; cambio aditivo, sin migración de BD).
- Un consumidor de fiabilidad observable (NFR1) debe leer `progress[step].status`
  para distinguir `done` de `degraded` (R-03 del review de dominio).

### CT3 — Contrato del endpoint `POST /api/v1/market/bid` (FR6)

- Entrada: `price: int` (query param), entre otros ya existentes.
- Precondiciones de validación en la frontera (antes de proxyar a Futmondo):
  - `price <= 0` → **HTTP 422** (ya existente, se mantiene).
  - `price > PRICE_SANITY_CAP` → **HTTP 422** (nuevo). `PRICE_SANITY_CAP` es una
    constante documentada (valor exacto en functional-design; R-03).
- Sin cambios en el contrato de salida (éxito/fracaso de la puja) ni en el frontend.

### CT4 — Política de `except` (FR3.2, no es una interfaz pública)

No introduce contrato de API; fija la semántica interna: en arranque/migraciones +
camino de sync en alcance, recuperable = log + continuar/reintentar; fatal =
propagar con contexto. La tabla por locus se cierra en functional-design.

## Sources

- Consume `inception/domain-design/components.md` (C1-C5) y `decisions.md` (ADR-1..4), `inception/requirements-analysis/requirements.md` (FR3.1/FR3.2/FR6).
- Código verificado: `task_manager.py` (`update_progress`, `progress`), `market.py::place_bid`.

## Assumptions & Open Questions

- Valor exacto de `PRICE_SANITY_CAP` y tabla recuperable/fatal por locus: functional-design.
