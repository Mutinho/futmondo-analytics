# Performance Requirements — Intent 4 (gate CI/CD hardening)

Run a nivel de workflow (scope infra, config-only de CI/CD). Este intent **no
toca el runtime de la aplicación**; las NFR de rendimiento de la app (latencia
de endpoints, throughput, utilización de recursos del servicio) **no aplican** y
no cambian respecto a la línea base en producción.

La única dimensión de rendimiento relevante es la **del propio gate de CI**, por
la restricción dura de coste 0 € (free tier de GitHub Actions).

| ID | Requisito | Objetivo / criterio pass-fail | Origen |
|----|-----------|-------------------------------|--------|
| NFR1.1 | Coste del gate dentro del free tier | El coste añadido de medir cobertura backend en dos jobs (PR `ci.yml` + push `verify`) y correr audits/lint no debe hacer superar el allowance mensual gratuito de GitHub Actions. Se cuantifica en FR16. | NFR1 (coste 0 €), FR16 |
| NFR1.2 | Sin regresión relevante de duración del pipeline | Añadir `--cov` a `verify`, los pasos de audit y `ruff check` no debe degradar de forma desproporcionada el tiempo de `verify`/`quality` (audits y lint son de segundos; la cobertura ya se mide en `ci.yml`). Criterio: duración de `verify` tras el cambio ≈ duración de `ci.yml` equivalente (misma clase de trabajo). | FR14, FR16 |

## Requisitos de runtime — N/A (con justificación)

- **Latencia/throughput de endpoints, utilización de CPU/memoria del servicio,
  benchmarks de la app**: N/A. Este intent solo modifica configuración de CI/CD y
  tooling; no altera el código de la aplicación ni su comportamiento en
  ejecución.

## Sources

- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/requirements-analysis/requirements.md` (NFR1, FR14, FR16).
- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md`.

## Assumptions & Open Questions

- El valor concreto de minutos de Actions consumidos y el margen de free tier se cuantifican en FR16 (documentación) y no bloquean esta etapa.
