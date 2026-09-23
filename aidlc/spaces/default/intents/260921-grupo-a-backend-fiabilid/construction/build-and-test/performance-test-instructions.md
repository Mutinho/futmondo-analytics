# Instrucciones de tests de rendimiento — Fiabilidad de la sync

> Conversation language: Spanish. Estado: **NO APLICA** para esta unidad.

## Aplicabilidad

No existe requisito NFR de rendimiento (carga, latencia, throughput) para esta
intervención. El intent es backend-only y aditivo: un helper de estado
degradado, un techo de validación de entero y el estrechamiento de unos
`except`. Ninguno introduce una ruta caliente nueva ni cambia el perfil de
rendimiento de la sync (que sigue dominada por las llamadas de red a Futmondo,
fuera de alcance).

Por tanto **no se generan ni ejecutan tests de rendimiento** en esta etapa. No
hay target de rendimiento medible en el inventario (Step 1), así que la matriz
de verificación no incluye filas de rendimiento.

## Sources

- `inception/requirements-analysis/requirements.md` (sin NFR de rendimiento),
  `construction/sync-reliability/code-generation/code-summary.md`.

## Assumptions & Open Questions

None.
