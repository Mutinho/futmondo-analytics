# Instrucciones de Test de Performance — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Estrategia: Minimal.

## Aplicabilidad

No aplican pruebas de performance dedicadas. Este bugfix no introduce NFR de
latencia/throughput ni cambia el perfil de rendimiento: reordena el borrado y la
inserción dentro de una única transacción (el número de operaciones de BD no
crece; de hecho se elimina un `commit` intermedio). No hay etapa
`performance-validation` planificada en este scope.

## Consideración de rendimiento del cambio

El repoblado sigue haciendo las mismas llamadas a la API de Sofascore con el
mismo throttling (`_min_delay = 0.75s`). El swap transaccional mantiene el
INSERT batch (`execute_values`/`executemany`) ya existente. No se espera
degradación; no se requiere medición.
