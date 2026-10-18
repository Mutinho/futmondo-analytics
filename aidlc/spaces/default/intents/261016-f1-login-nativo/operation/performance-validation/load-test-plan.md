# Load Test Plan — F1: Login nativo end-to-end

> Fase: operación (performance-validation). Perspectiva de quality engineer. Idioma: castellano;
> tokens técnicos verbatim en inglés. F1 es un **ajuste de transporte aditivo** (D-01) sobre
> endpoints de auth ya existentes; **no introduce NFR de rendimiento/escalabilidad nuevos** (los
> NFR de F1 son seguridad, coste 0 €, verificación e idioma — ver `requirements.md`). El load test
> formal con herramientas gestionadas es de pago y **NO-APLICA** a coste 0 €; se valida con
> medición puntual gratuita.

## Alcance y enfoque

- **Qué se valida**: que el transporte D-01 no degrada la latencia ni rompe los endpoints de auth
  bajo uso normal (single-maintainer + unos pocos usuarios; sin pico ni burst esperados).
- **Qué NO se hace**: load test sostenido con generador gestionado (k6 Cloud, Gatling Enterprise,
  CloudWatch/X-Ray), pruebas de autoescalado ni de capacidad a gran escala — NO-APLICA (de pago y
  sin patrón de tráfico que lo justifique).

## Patrones de tráfico (realistas para el proyecto)

| Patrón | Estimación | Nota |
|--------|-----------|------|
| Steady state | muy bajo (handful de usuarios, logins esporádicos) | No es un servicio de alto QPS |
| Peak | login al abrir la app; auto-login al reabrir | Ráfaga trivial |
| Burst | no esperado | Sin eventos de tráfico masivo |

## Método de medición (gratuito, reproducible)

- **Latencia puntual** con `curl -w "%{time_total}"` contra:
  - `GET /health` (línea base del servidor).
  - `POST /auth/login` (ruta de auth; con credenciales inválidas para no requerir secretos, mide
    la ruta completa incl. validación contra Futmondo).
- **Observación** vía `fly logs`/`fly status` (ver `dashboards.md`).
- **Umbral de referencia (no contractual)**: `/health` < ~1 s en caliente; `/auth/*` dominado por
  el round-trip a la API de Futmondo, no por el transporte D-01.

## Objetivos de latencia (indicativos)

No hay percentiles p50/p95/p99 contractuales (requerirían métricas gestionadas de pago). Se usa la
medición puntual como evidencia de que no hay regresión perceptible.

## Sources

- [consumes] performance-requirements.md, scalability-requirements.md, performance-design.md,
  scalability-design.md — NO existen (nfr-requirements/nfr-design `skipped` para rendimiento;
  F1 no tiene NFR de rendimiento). dashboards.md (operation/observability-setup).
- [consumes] requirements.md (NFR de F1: seguridad/coste/verificación/idioma).
- [memory] aidlc-shared/operation-fly-stack.md (SLO/load de pago NO-APLICA); project.md (coste 0 €).

## Assumptions & Open Questions

None.
