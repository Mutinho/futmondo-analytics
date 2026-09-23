# Plan de load testing — Fiabilidad de la sync

> Conversation language: Spanish. Estado: **NO APLICA** para este intent.

## Aplicabilidad

No existe NFR de rendimiento (latencia, throughput, tráfico, saturación) para
esta intervención, ya documentado como NO-APLICA en
`construction/build-and-test/performance-test-instructions.md`. El intent es
backend-only y aditivo:

- `record_degraded_step`: escribe un dict de estado + emite un log — O(1).
- Techo `PRICE_SANITY_CAP`: una comparación de enteros — O(1).
- `except` acotados: cambian el manejo de errores, no el camino feliz.

Ninguno introduce una ruta caliente nueva ni altera el perfil de carga (que en
esta app lo domina la red a la API de Futmondo, fuera de alcance).

## Decisión

- **No se diseña ni ejecuta un plan de carga.** No hay objetivo de percentil,
  throughput ni escalado que validar.
- Sin CloudWatch/X-Ray (servicios de pago) — irrelevante aquí porque no hay
  target de rendimiento que medir.

## Qué se valida en su lugar

Las NFRs reales del intent (NFR1-NFR5) se validan en `nfr-validation-matrix.md`
con la evidencia existente (suite `pytest`, código, logs), a coste 0 €.

## Sources

- `construction/build-and-test/performance-test-instructions.md` (NO-APLICA),
  `inception/requirements-analysis/requirements.md` (sin NFR de rendimiento),
  `construction/sync-reliability/code-generation/code-summary.md`.

## Assumptions & Open Questions

None.
