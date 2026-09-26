# Scalability Design — Intent 4 (gate CI/CD hardening)

> Etapa de diseño: patrones y decisiones, no implementación.

## Alcance

Este intent es **config-only de CI/CD** y **no cambia la escalabilidad de la
aplicación** (usuarios concurrentes, volumen de datos, estrategia de scaling de
Fly.io/Neon). Las NFR de escalabilidad de runtime **no aplican** y no cambian
respecto a la línea base en producción.

## Runtime de la app — N/A (justificado)

Carga de usuarios concurrentes, proyecciones de crecimiento, triggers de
escalado, capacidad y crecimiento de datos: **N/A**. El intent no toca el código
de la aplicación, la BD (Neon) ni la topología de despliegue (dos apps Fly.io);
su escalabilidad es la misma que antes del intent.

## Dimensión análoga a escalabilidad: volumen de deuda heredada del gate

La única dimensión que se comporta como "escalabilidad" es el **volumen de deuda
heredada que cada promoción advisory→bloqueante reportaría de golpe**. El diseño
lo gobierna con **promoción escalonada** para acotar ese "volumen de rojos":

- **Audits**: si `npm audit --audit-level=high` reporta demasiada deuda de golpe,
  se promueve primero en `critical`, se sanea, y luego se endurece a `high`
  (trinquete de severidad que sólo endurece).
- **Lint**: la deuda que `ruff check` reporte hoy en advisory se sanea **por
  fichero de forma quirúrgica** o se suprime con `per-file-ignores`/`# noqa`
  puntual con rationale ANTES de bloquear. Nunca ampliando/reescribiendo los
  god-files ni con `--fix` de repo entero.
- **Aislamiento**: cada promoción va en su propio commit `chore(ci)`, de modo
  que el "lote" de deuda que introduce cada endurecimiento es acotado y
  revertible por separado.

Esto acota el volumen de fallos que la promoción introduce sin ser una NFR de
scaling de sistema.

## Diseño stateless del gate (buena práctica aplicable)

Los jobs del gate son **stateless e idempotentes**: cada ejecución parte del
código en el commit y del entorno resuelto por instalación, sin estado
compartido entre ejecuciones. Esto ya es así y se preserva; refuerza la
reproducibilidad (NFR5.1) y permite que PR-gate y push-gate corran de forma
independiente sin coordinación de estado.

## Trazabilidad

- Escalabilidad de runtime → N/A (justificado).
- Volumen de deuda de promoción → promoción escalonada (deriva de FR12).

## Sources

- `../nfr-requirements/scalability-requirements.md` (N/A justificado; nota de volumen de deuda).
- `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md` (topología en producción, sin cambios).

## Assumptions & Open Questions

- None.
