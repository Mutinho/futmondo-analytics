# Entidades — U1 sync-reliability

> Conversation language: Spanish. Backend-only. El intent no introduce entidades
> de dominio nuevas ni tablas; opera sobre estructuras existentes de forma aditiva.

## Entidades / estructuras afectadas

| Entidad | Naturaleza | Cambio |
|---|---|---|
| `progress[step]` (dict dentro de `Task`/`TaskRecord`) | Estado por-paso de la sync, JSON libre | Aditivo: admite `status: "degraded"` + `reason` |
| `StepStatus` (nuevo) | Enum de valores de estado de paso (`running`/`done`/`degraded`) | Nuevo, en `sync_step_status.py` |
| `PRICE_SANITY_CAP` (nuevo) | Constante de módulo en `market.py` | Nuevo, techo de validación |

- Sin cambios de esquema de BD: `TaskRecord.progress` ya es JSON libre.
- Sin entidades de dominio nuevas (no hay tablas ni modelos nuevos).

## Sources

- `functional-spec.md` (FS1-FS4), `inception/domain-design/components.md`.

## Assumptions & Open Questions

None.
