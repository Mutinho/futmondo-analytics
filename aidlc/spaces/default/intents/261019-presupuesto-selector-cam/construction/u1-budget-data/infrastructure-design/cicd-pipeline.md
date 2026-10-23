# Infrastructure Design — CI/CD (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA infraestructura/CI-CD nuevo.** U1 es código de una librería cliente iOS (`FutmondoKit/Budget/`) que:
- No despliega nada: no toca Fly.io, Neon, ni la topología de producción.
- No añade jobs ni modifica los workflows (`ci.yml`, `fly-deploy.yml`). El gate de CI bloqueante existente (gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`) aplica al PR tal cual; un cambio de código Swift no dispara pisos backend/frontend ni requiere pasos nuevos.
- La verificación de U1 es `cd ios && swift build && swift test`, ejecutada en WSL por el desarrollador (no hay runner Swift en el CI actual, y no se añade: coste 0 € y fuera del alcance de este intent).

## Decisión

Ninguna infraestructura ni pipeline nuevo. Si en el futuro se quisiera CI para el paquete iOS, sería un intent aparte (runner macOS/Swift), hoy no justificado (single-maintainer, verificación local + dispositivo).

## Riesgo/deuda aceptada

La verificación de U1 (`swift build && swift test`) es una **garantía manual local** (WSL), **sin control automatizado en el PR** (el gate de CI existente no ejecuta Swift). Se registra explícitamente como **deuda/riesgo aceptado**: NO-APLICA aquí significa "no hay infra/CI nuevo que diseñar", no "nada que verificar" — la verificación existe y es responsabilidad del desarrollador antes del checkpoint. Un runner Swift en CI queda como follow-up (intent aparte).

## Sources

- `aidlc/spaces/default/memory/team.md` (gate de CI, deploy on-merge; este intent no despliega)
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-design/logical-components.md`

## Assumptions & Open Questions

None.
