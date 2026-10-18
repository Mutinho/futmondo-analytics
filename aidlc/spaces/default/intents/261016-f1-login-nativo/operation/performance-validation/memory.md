<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
2026-10-18 — F1 no declara NFR de rendimiento/escalabilidad: performance-validation se enfoca en no-regresión del transporte D-01 con medición puntual gratuita (curl -w), no en cumplimiento de SLO. NFR de F1 reales: seguridad/coste/verificación/idioma.

## Deviations
2026-10-18 — Load test sostenido / autoescalado / percentiles con métricas gestionadas marcados NO-APLICA (de pago, sin patrón de tráfico que lo justifique); sustituidos por mediciones curl reales contra prod.
2026-10-18 — performance/scalability-requirements y -design no existen (etapas skipped); evidencia derivada de la app desplegada + mediciones en vivo + resultados de construcción.

## Tradeoffs
2026-10-18 — Medición puntual (3 muestras /health + 1 /auth/login 401) en vez de carga sostenida: suficiente para evidenciar que D-01 no añade latencia material; la latencia de /auth/login está dominada por el round-trip a Futmondo, no por el transporte.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
