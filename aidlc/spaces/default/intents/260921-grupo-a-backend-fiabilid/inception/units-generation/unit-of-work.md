# Units Generation — Unidades de trabajo (grupo-a-backend-fiabilidad)

## Sources

- `components.md` (C1-C5) y `decisions.md` (ADR-1..4) del diseño de dominio.
- `requirements.md` (FR3.1, FR3.2, FR6, NFR1-5).

## Decomposición

El intent es una intervención acotada sobre un único servicio desplegable (el
backend FastAPI `futmondo-api`). Los cinco componentes del diseño (helper de paso
degradado, valor `degraded`, cableado en `sync.py`, política de `except`, techo de
`price`) viven en el mismo servicio y se despliegan juntos; no hay decomposición
en varias unidades viable ni deseable, ni paralelismo que explotar. Por tanto:
**una sola unidad de trabajo**.

## Unidades

| Unit ID | Directory | Nombre | Kind | Complejidad | Deployment |
|---|---|---|---|---|---|
| U1 | u1-sync-reliability | sync-reliability | service | M | shared (backend `futmondo-api`) |

```yaml
units:
  - name: sync-reliability
    kind: service
    depends_on: []
```

### U1 — sync-reliability

- **Descripción**: Fiabilidad observable de la sync (estado `degraded` para
  `prizes`/`phantoms` vía helper estrecho), `except` acotados en
  arranque/migraciones + camino de sync, y techo de sanidad del `price` de puja.
- **Responsabilidades**:
  - Helper `record_degraded_step` (C2) + valor `StepStatus.DEGRADED` (C1), fuera del god-file.
  - Cableado de `prizes`/`phantoms` al helper en `sync.py` (C3).
  - Política `except` recuperable/fatal en arranque/migraciones + camino de sync (C4).
  - Techo `PRICE_SANITY_CAP` en `place_bid` (C5).
- **Kind**: `service` — código dentro del ejecutable desplegado `futmondo-api`.
- **Deployment**: compartido (no es un servicio nuevo).
- **Complejidad**: M — varias piezas aditivas coherentes + specs `pytest`.
- **Notas/constraints**:
  - No ampliar los god-files (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router.
  - Cambios aditivos, sin migración de BD. Backend-only. Coste 0 €.
  - Specs `pytest` significativas (estado de tarea, log, recuperable/fatal, rechazo por techo).

## Assumptions & Open Questions

None.
