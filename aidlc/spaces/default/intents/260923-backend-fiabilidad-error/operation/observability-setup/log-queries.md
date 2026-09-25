# Log Queries — Observabilidad (FR3.2 + FR4)

Consultas operativas sobre el **logging estructurado clave=valor** que introdujo
este intent (NFR1), a coste 0 € con `fly logs` + `grep`. Este es el plano de
consulta real del proyecto (sin agregador de pago). Los campos emitidos por
`_log_integration_failure`: `sync_step`, `failure_mode`, `status`, `endpoint`,
`task_id`, `reason`. Nunca hay credenciales en los logs (NFR3).

## Base

```bash
# Logs en vivo del backend
fly logs --app futmondo-api

# Logs recientes (volcado) para grep offline
fly logs --app futmondo-api > /tmp/api.log
```

## Consultas por caso de uso

| Objetivo | Comando |
|---|---|
| Todos los fallos de integración (recuperable + fatal) | `fly logs --app futmondo-api \| grep 'failure_mode='` |
| Solo fallos **fatales** (baneo, etc.) | `fly logs --app futmondo-api \| grep 'level=ERROR' \| grep 'failure_mode='` |
| Solo **recuperables / DEGRADED** | `fly logs --app futmondo-api \| grep -E 'failure_mode=(timeout\|unparseable\|request_exception)'` |
| Baneo de Sofascore (403) | `fly logs --app futmondo-api \| grep 'failure_mode=ban'` |
| Reconstruir un sync concreto por `task_id` | `fly logs --app futmondo-api \| grep 'task_id=<ID>'` |
| Ver qué paso degradó | `fly logs --app futmondo-api \| grep -E 'failure_mode=' \| grep -oE 'sync_step=[^ ]+'` |
| Estado del proceso / apps | `fly status --app futmondo-api` |
| Salud del release | `curl -sS https://futmondo-api.fly.dev/health` |

## Interpretación

- **`level=WARNING failure_mode=…`** → fallo **recuperable**: el paso se marcó
  `DEGRADED` y el sync continuó. Esperado ante timeout/respuesta no parseable
  puntual; sólo es señal si aparece de forma **inesperada o repetida**.
- **`level=ERROR failure_mode=ban`** (o fatal) → fallo **fatal**: el paso abortó
  limpio (sin datos a medias). Requiere atención (posible baneo de IP).
- **Ausencia de `failure_mode=`** en un sync completo → ejecución sana.

## Retención

- `fly logs` es un stream/buffer reciente (sin retención gestionada de pago). Para
  conservar un incidente, volcar a fichero (`fly logs > archivo.log`) durante el
  análisis. Sin coste recurrente.

## Assumptions & Open Questions

None.
