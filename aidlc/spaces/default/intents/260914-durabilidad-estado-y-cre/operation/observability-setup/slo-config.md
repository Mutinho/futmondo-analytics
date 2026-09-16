# SLO Config — Durabilidad del estado (NO-APLICA a coste 0 €)

> Etapa Observability Setup (Operation). Los SLO formales con error budget y burn-rate multi-ventana
> requieren un sistema de métricas/alerting de pago (CloudWatch, Grafana Cloud, Datadog). Bajo el
> mandato dura de coste 0 € y con NFR2 sin umbral numérico definido, NO se configuran SLO formales en
> este intent. Se documenta el enfoque diferido y el objetivo cualitativo actual.

## Estado: NO-APLICA a coste 0 € (diferido)

- **Motivo**: sin infraestructura de métricas de pago; NFR2 (rendimiento) no fija umbral numérico
  ("se validará por medición"). Un SLO sin medición continua ni error budget sería nominal.

## Objetivo de disponibilidad cualitativo (actual)

- El healthcheck `/health` de Fly.io + el smoke test del pipeline son la verificación de release y la
  señal de disponibilidad básica. Fly reinicia la máquina ante 3 fallos consecutivos del check.
- No se compromete un porcentaje numérico de disponibilidad (99.x%) porque no se mide de forma
  continua a coste 0 €.

## SLI candidatos si se graduara a un tier de pago (futuro)

| SLI | Definición | Ventana sugerida |
|-----|------------|------------------|
| Disponibilidad backend | `2xx+3xx / total` en `/api/v1/*` | 30 días rolling |
| Rehidratación de sesión | `sesiones reconstruidas OK / intentos tras reinicio` | 30 días rolling |
| Latencia camino sesión | `peticiones < umbral / total` (fijar umbral en NFR2) | 30 días rolling |

## Recomendación

- Si el proyecto adopta un tier de pago o una herramienta gratuita de métricas con retención, fijar
  primero el umbral de NFR2 por medición (ver `performance-validation`) y luego derivar el SLO y el
  error budget. Hasta entonces, la observabilidad es cualitativa por healthcheck + logs.
