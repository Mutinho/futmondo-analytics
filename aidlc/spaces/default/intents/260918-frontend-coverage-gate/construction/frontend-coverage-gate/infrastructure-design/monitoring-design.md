# Diseño de Monitorización — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). La "observabilidad" relevante de este intent es la **señal de cobertura de tests en CI**, no monitorización de runtime de un servicio.

## Observabilidad de la cobertura (en CI)

- **Señal**: el reporte de cobertura por métrica (`lines`, `branches`, `functions`, `statements`) que `ng test` produce sobre `src/app/**` en cada ejecución de `ci.yml` (PR) y `verify` (push).
- **Enforcement vs observabilidad**: el **enforcement** (fallar si una métrica cae por debajo del umbral) vive dentro de `ng test` y es bloqueante. Cualquier paso adicional de **reporte** (imprimir el resumen, subir un artefacto de cobertura) es solo observabilidad y no bloqueante; nunca lleva `continue-on-error` que sustituya el enforcement (NFR1.5).
- **Ratchet visible**: el umbral por métrica en `angular.json` es la línea base observable; su evolución (solo hacia arriba, revisada por MR) documenta el progreso de cobertura.
- **Coste 0 €**: el reporte se genera y consume dentro de `ng test` en el runner free-tier; no se usa Codecov/Coveralls ni ningún servicio de pago.

## Monitorización de runtime — NO-APLICA

- SLO formales con burn-rate, tracing distribuido, dashboards de métricas de servicio, alerting: **NO-APLICA** para una unidad `packaging` sin runtime propio, y quedarían fuera del mandato de coste 0 € (aprendizaje afirmado en `project.md` para stack Fly.io + Neon). El healthcheck `/health` del despliegue Fly.io existente (smoke test, 5 reintentos HTTP 200) permanece **sin cambios** y no es responsabilidad de este intent.

## Assumptions & Open Questions

- None.
