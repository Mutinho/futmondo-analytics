# Instrucciones de Test de Integración — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Estrategia: Minimal.

## Aplicabilidad

Bajo la estrategia **Minimal** de este bugfix no se generan suites de
integración dedicadas: el comportamiento afectado (endpoint `sync_sofascore` y
cliente Sofascore) queda cubierto por la regresión dirigida a nivel de unidad en
`backend/tests/test_sofascore_sync_characterization.py`, que ejercita el flujo
completo del endpoint con fakes de `db` y de los clientes externos (verificando
el orden transaccional DELETE→INSERT en una sola conexión).

## Cómo se cubre el límite de integración

El punto de integración crítico es la transacción de reemplazo de caché frente a
la capa `db_connection.py`. Se verifica de forma equivalente con un fake de `db`
que registra el orden de operaciones en la misma conexión (ver
`unit-test-instructions.md`, casos de endpoint). Una prueba de integración real
contra Neon PostgreSQL requeriría credenciales y entorno con coste; queda fuera
de alcance por la regla de coste 0€ (NFR2) y la superficie mínima (NFR3).
