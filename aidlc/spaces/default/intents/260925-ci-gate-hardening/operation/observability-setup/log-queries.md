# Log Queries — Intent 4 (gate CI/CD hardening)

> Fase Operation. Las CloudWatch Logs Insights queries del conocimiento **no
> aplican** (de pago). Se documentan equivalentes con las herramientas gratuitas
> (`fly logs` + `grep`/filtros; log de GitHub Actions) (Q5=A).

## Consultas de runtime (`fly logs` + `grep`)

Los logs son estructurados (campos como `sync_step`, `reason`, `task_id`, nivel).
Ejemplos (ilustrativos, ≤15 líneas):

```bash
# Errores recientes del backend
fly logs --app futmondo-api | grep -iE 'error|traceback'

# Seguir un sync por task_id
fly logs --app futmondo-api | grep 'task_id=<id>'

# Pasos de sync marcados degraded
fly logs --app futmondo-api | grep 'DEGRADED'

# Salud del healthcheck (peticiones a /health)
fly logs --app futmondo-api | grep '/health'
```

## Consultas del estado del gate (log de GitHub Actions)

En la vista de un workflow run (o `gh run view <id> --log`):

| Qué buscar | Cómo |
|------------|------|
| Paso del gate que falló | filtrar por el nombre del step (`pip-audit (blocking)`, `ruff check (blocking)`, `coverage floor`, …) |
| Finding de audit | buscar la salida de `pip-audit` / `npm audit` en su step |
| Entrada de allowlist caducada | buscar `::error::...expired` del step de expiry |
| Rojo de cobertura | buscar el mensaje de `--cov-fail-under` en el step de pytest |

## Retención

- `fly logs` es un stream (retención limitada del plan free); para incidencias,
  capturar el fragmento relevante al momento. Sin agregador gestionado de pago.
- El log de GitHub Actions se retiene según el plan (free) del repo.

## NO-APLICA (de pago) — documentado

- **CloudWatch Logs Insights** (`filter`/`stats`/`parse`): NO-APLICA (coste).
  Sustituido por `fly logs` + `grep` y el log de Actions.
- **Agregador gestionado / retención a S3+Glacier**: NO-APLICA (coste).

## Sources

- `../../construction/nfr-design/observability-design.md` (logs estructurados, `task_id`).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- La retención de `fly logs` está limitada por el free tier; para diagnóstico se captura el fragmento en el momento.
