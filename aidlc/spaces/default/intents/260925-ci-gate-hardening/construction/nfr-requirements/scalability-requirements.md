# Scalability Requirements — Intent 4 (gate CI/CD hardening)

Este intent es config-only de CI/CD y **no cambia la escalabilidad de la
aplicación** (usuarios concurrentes, volumen de datos, estrategia de scaling de
Fly.io/Neon). Las NFR de escalabilidad de runtime **no aplican** y no cambian
respecto a la línea base en producción.

## Requisitos de runtime — N/A (con justificación)

- **Carga de usuarios concurrentes, proyecciones de crecimiento, triggers de
  escalado, capacidad, crecimiento de datos**: N/A. El intent no toca el código
  de la aplicación, la BD (Neon) ni la topología de despliegue (dos apps Fly.io);
  su escalabilidad es la misma que antes del intent.

## Nota de "escalabilidad" del gate (no es una NFR de scaling clásica)

La única dimensión análoga a escalabilidad es el **volumen de deuda heredada**
que cada promoción advisory→bloqueante reportaría de golpe:

- Si `npm audit --audit-level=high` o `ruff check` bloqueante reportan demasiada
  deuda heredada de una vez, la promoción es escalonada (FR12): primero
  `critical` en npm, sanear, luego `high`; la deuda de lint se sanea por fichero
  de forma quirúrgica o se suprime con `per-file-ignores`/`# noqa` puntual antes
  de bloquear. Esto acota el "volumen" de rojos que la promoción introduce, sin
  ser una NFR de scaling de sistema.

## Sources

- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/requirements-analysis/requirements.md` (FR12).
- `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md` (topología en producción, sin cambios).

## Assumptions & Open Questions

- None.
