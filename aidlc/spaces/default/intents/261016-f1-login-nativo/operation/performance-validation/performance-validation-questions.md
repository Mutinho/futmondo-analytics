# Performance Validation — Preguntas y confirmación — F1: Login nativo end-to-end

> Fase: operación (performance-validation). Idioma: castellano; tokens técnicos verbatim en inglés.

## Preguntas de clarificación

- **¿Patrones de tráfico?** Muy bajo (handful de usuarios, logins esporádicos + auto-login al
  reabrir); sin pico ni burst esperados.
- **¿Percentiles objetivo (p50/p95/p99)?** No contractuales: F1 no declara NFR de latencia; medición
  puntual como evidencia de no-regresión (métricas gestionadas de pago NO-APLICA).
- **¿Throughput a sostener?** No es un servicio de alto QPS; sin requisito de throughput.
- **¿Cuellos de botella probables?** `/auth/login` está dominado por el round-trip a la API de
  Futmondo, no por el transporte D-01 (serialización en memoria, coste despreciable).

## Consolidated Summary Confirmation

Resumen de lo producido en performance-validation para F1:

- **load-test-plan.md**: validación **ligera y gratuita** (F1 es transporte aditivo sin NFR de
  rendimiento). Load test sostenido / autoescalado / percentiles gestionados: NO-APLICA (de pago,
  sin patrón de tráfico que lo justifique).
- **test-results.md**: mediciones reales 2026-10-18 contra prod — `/health` ~0.18 s en caliente
  (HTTP 200); `POST /auth/login` con credencial inválida 401 en ~0.42 s (dominado por Futmondo).
  D-01 no añade latencia material; sin regresión.
- **nfr-validation-matrix.md**: NFR-1 (seguridad), NFR-2 (coste 0 €), NFR-3 (verificación: pytest
  422 + swift test 29 + validación en dispositivo), NFR-4 (idioma) — todos ✅ cumplen; rendimiento
  ✅ sin regresión.

No se inventa infraestructura: performance/scalability-requirements y -design no existen (etapas
`skipped`; F1 sin NFR de rendimiento). Evidencia derivada de la app desplegada, mediciones en vivo
y resultados de construcción.

¿Es todo correcto?

[Answer]: Looks correct
