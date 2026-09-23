# Documento de alcance — Fiabilidad de la sync de 11 pasos

> Conversation language: Spanish. Scope: `feature`. Brownfield futmondo-analytics.
> Consume `intent-statement.md` (etapa intent-capture). Reencuadre Opción C.

## En alcance (IN)

1. **FR3.1 — Visibilidad de pasos degradados `prizes` y `phantoms`.**
   - Un helper estrecho y reutilizable (p. ej. `record_degraded_step(task, step, reason)`)
     que registra el fallo de un paso "non-critical" en **dos canales**: log
     estructurado y **estado del paso "degradado" en la tarea** (in-memory
     `TaskManager` y el `task_service` durable).
   - Aplicado a los pasos `prizes` y `phantoms`, que hoy reportan éxito aunque el
     paso falle.
   - El helper vive **fuera** del god-file, en una función/módulo estrecho testeable.

2. **FR3.2 — Acotar el `except Exception`/bare-except silencioso.**
   - Arranque y migraciones (`services/db_connection.py`, `auth/token_store.py` y
     equivalentes) + los `except` del camino de sync tocado por FR3.1.
   - Distinguir recuperable (log + continuar/reintentar) de fatal (propagar). Nada
     de capturar-y-silenciar en esos puntos.

3. **FR6 (remate) — Techo de sanidad del `price` de puja.**
   - Añadir un techo superior a la validación ya existente (`price <= 0` → 422) en
     `market.py::place_bid`, con su test de regresión.

4. **Tests `pytest` significativos** para las tres piezas (estado de tarea + log en
   FR3.1; recuperable/fatal en FR3.2; rechazo por techo en FR6), con aserciones
   reales, nunca `assert True`.

## Fuera de alcance (OUT)

- **Frontend**: no se toca (la validación de `price` del frontend ya existe).
- **Rango dinámico min/max del mercado** para FR6 (acopla al estado del campeonato / god-file; coste).
- **Purga masiva** de los ~159 `except` del backend (solo arranque/migraciones + camino de sync).
- **Reescritura o descomposición de god-files** (`data_sync_service.py`, `data_manager_v2.py`) — es FR13, otro intent.
- **Los demás pasos "non-critical"** de la sync distintos de `prizes`/`phantoms` (el helper deja la puerta abierta a rondas futuras).
- **Cambio de esquema de BD mayor** para el estado de tarea (se busca un cambio aditivo mínimo; se confirma en diseño).

## Restricciones

- Backend-only; coste 0 € (tiers gratuitos); no ampliar god-files ni el patrón SQL-en-router.
- Gate de CI bloqueante (gitleaks + `pytest` + `ng test`) verde antes de merge; squash-merge; Conventional Commits en castellano.
- Formateo brownfield quirúrgico: no reformatear en masa ficheros existentes.

## Notas para diseño (hallazgos del reviewer, no bloqueantes)

- **R-01**: el locus real de FR3.1 es el bucle de pasos de la sync (`sync.py` ~144-164
  para `prizes`/`phantoms`), no `data_sync_service.py:224` (ese es
  `_enrich_market_values`, otro paso). Confirmar el fichero exacto en
  reverse-engineering/domain para no desviar el diseño hacia el god-file.
- **R-02**: fijar el **contrato tipado** del estado "degradado" de la tarea para que
  las specs puedan aseverar el estado, no solo el log.
- **R-03**: acotar el **criterio del techo** de `price` (p. ej. múltiplo holgado del
  presupuesto máximo plausible) para que el test asevere un límite estable.

## Sources

- [desc] Reencuadre Opción C confirmado por el usuario.
- Consume `ideation/intent-capture/intent-statement.md`.
- Hallazgos R-01/R-02/R-03 de la revisión advisory de intent-capture
  (`.aidlc-reviews/intent-capture/stage/ea04c38435cec6e6/1.review.md`).

## Assumptions & Open Questions

- El fichero exacto del bucle de pasos (`sync.py` vs `data_sync_service.py`) se
  confirma en la etapa de análisis/diseño; no altera el alcance.
