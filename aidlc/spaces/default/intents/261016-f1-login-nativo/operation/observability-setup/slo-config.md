# SLO / SLI Config — F1: Login nativo end-to-end

> Fase: operación (observability-setup). Idioma: castellano; tokens técnicos verbatim en inglés.
> **Sin SLO formal con error budget / burn-rate** (requiere observabilidad gestionada de pago =
> NO-APLICA a coste 0 €). Se define un **SLI informal** verificable con herramientas gratuitas,
> coherente con `aidlc-shared/operation-fly-stack.md`.

## SLI informal (medible gratis)

| SLI | Definición | Medio de medición | Objetivo indicativo (no contractual) |
|-----|------------|-------------------|--------------------------------------|
| Disponibilidad del backend | `/health` devuelve HTTP 200 | `curl` puntual / smoke del CD | 200 en condiciones normales |
| Éxito de login nativo | `POST /auth/login` devuelve 200 + `refresh_token` en body | validación en dispositivo + `fly logs` | login correcto desde la app |
| Éxito de refresh | `POST /auth/refresh` renueva el access token | auto-login en la app + `fly logs` | sesión recuperada tras reabrir |
| Ausencia de errores de auth | sin picos de 4xx/5xx en `/auth/*` | `fly logs \| grep` (pull) | sin picos inesperados |

## Por qué no hay SLO formal

- Un SLO formal (p. ej. "99.9% disponibilidad en ventana de 30 días") con **error budget** y
  **alertas por burn-rate** exige métricas gestionadas con retención y agregación, que en este
  stack serían de pago. El mandato de **coste 0 €** lo descarta; se marca **NO-APLICA** y se
  sustituye por el SLI informal de arriba (regla durable de adaptación de Operation).
- El objetivo indicativo no es un compromiso con error budget; es una referencia operativa para el
  mantenedor único.

## Relación con F1 (D-01)

D-01 es aditivo y retrocompatible: no degrada los SLI existentes. El nuevo canal (refresh token por
body/header) se observa dentro del SLI "éxito de refresh" sin métrica nueva de pago.

## NO-APLICA (de pago)

| Concepto del stage | Estado |
|---|---|
| SLO formal con error budget | NO-APLICA; sustituido por SLI informal |
| Alertas por burn-rate | NO-APLICA (ver `alarms.md`) |
| Retención/agregación de métricas gestionada | NO-APLICA; observación pull |

## Sources

- [consumes] performance-design.md, reliability-design.md — NO existen (`skipped`); derivado de la
  app desplegada y de health-check-report.md.
- [memory] aidlc-shared/operation-fly-stack.md (SLI informal, SLO de pago NO-APLICA);
  phases/operation.md (SLO cuantificado con % y ventana — aquí marcado NO-APLICA con rationale);
  project.md (coste 0 €).

## Assumptions & Open Questions

None.
