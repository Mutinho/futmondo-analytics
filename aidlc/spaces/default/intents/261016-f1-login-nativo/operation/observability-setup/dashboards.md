# Dashboards — F1: Login nativo end-to-end

> Fase: operación (observability-setup). Perspectiva de operations engineer. Idioma: castellano;
> comandos y claves verbatim en inglés. El stack es Fly.io + Neon (coste 0 €, single-maintainer):
> **no hay CloudWatch ni dashboards gestionados** (serían de pago). La observabilidad es **pull**
> con herramientas gratuitas. Adaptación según `aidlc-shared/operation-fly-stack.md`.

## Superficie observable de F1

F1 añade un transporte de refresh token (D-01) sobre endpoints de auth ya existentes. La superficie
a observar es `/auth/login`, `/auth/refresh`, `/auth/logout` y la salud general del backend.

## "Dashboard" pull (comandos gratuitos)

En vez de un dashboard gestionado, el operador usa estos comandos (coste 0 €):

| Vista | Comando | Qué muestra |
|-------|---------|-------------|
| Salud del backend | `curl -sS https://futmondo-api.fly.dev/health` | 200 `{"status":"healthy"}` |
| Estado de máquinas | `fly status --app futmondo-api` | estado/región/releases |
| Logs en vivo | `fly logs --app futmondo-api` | stream de logs de la app |
| Auth (filtrado) | `fly logs --app futmondo-api \| grep -E "/auth/(login\|refresh\|logout)"` | actividad de auth |
| Frontend | `fly status --app futmondo-app` + `curl -sS -o /dev/null -w "%{http_code}" https://futmondo-app.fly.dev/` | disponibilidad PWA |

## Golden signals (lo que se observa, con el medio gratuito)

| Señal | Medio gratuito | Nota |
|-------|----------------|------|
| Latencia | `time_total` de `curl` puntual a `/health` y `/auth/*`; tiempos en `fly logs` | Sin histograma gestionado (NO-APLICA de pago) |
| Tráfico | conteo de líneas de `/auth/*` en `fly logs` | Pull manual |
| Errores | `fly logs ... \| grep -E "( 4[0-9]{2}\| 5[0-9]{2}\|ERROR)"` | Sin agregación gestionada |
| Saturación | `fly status` (CPU/mem de la máquina Fly.io) | Métrica básica de la plataforma |

## NO-APLICA (de pago) y su sustituto gratuito

| CloudWatch (stage) | Sustituto gratuito | Estado |
|---|---|---|
| Dashboards gestionados | comandos `fly`/`curl` + logs estructurados | Sustituido |
| Metrics con retención/gráficas | observación pull puntual | NO-APLICA (ML/retención de pago) |

## Sources

- [consumes] performance-design.md, security-design.md, reliability-design.md, monitoring-design.md,
  infrastructure-specification.md — NO existen (nfr-design/infrastructure-design `skipped` en los 3
  bolts); se deriva de la app desplegada y de deployment-execution.
- [consumes] health-check-report.md, smoke-test-results.md (operation/deployment-execution).
- [memory] aidlc-shared/operation-fly-stack.md (mapeo AWS→gratuito); project.md (coste 0 €);
  phases/operation.md (métrica de salud + error rate).

## Assumptions & Open Questions

None.
