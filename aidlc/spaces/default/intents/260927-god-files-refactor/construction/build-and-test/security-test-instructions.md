# Instrucciones de Tests de Seguridad — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, test strategy **Minimal**. Conversation language: Spanish. Perspectiva de seguridad (DevSecOps) integrada.

## Aplicabilidad

**N/A como suite de seguridad nueva en esta oleada.** No hay requisitos NFR de seguridad nuevos ni superficie de ataque nueva: el refactor preserva el comportamiento observable, no toca autenticación/autorización (los endpoints y `get_service()` quedan intactos), y no introduce dependencias nuevas (BR5.1).

## Comprobaciones de seguridad que SÍ siguen vigentes (heredadas del gate)

Desde la perspectiva del ingeniero de seguridad, el gate de CI bloqueante existente cubre lo relevante y no se debilita:

- **gitleaks** escanea el repo incluidos los tests: los tests nuevos (`test_analytics_service.py`) usan dobles in-memory y NO contienen credenciales/tokens reales (FR3.3, NFR3). El `JWT_SECRET` usado en build/test es efímero y no productivo.
- **SQL isolation (BR2.2)**: el SQL crudo queda confinado en `data_manager_adapter.py` con parámetros vía `adapt_params` (placeholders parametrizados `?`→`%s`), sin concatenación de entrada de usuario; no se introduce SQL-en-router nuevo.
- **Sin secretos en claro**: la extracción no mueve ni expone credenciales; `AnalyticsService` no maneja password/token Futmondo.

## Nota

No hay comando SAST/DAST específico que ejecutar en esta oleada más allá del gate existente (gitleaks + `pytest` + `ng test`), que se re-ejecuta en CI antes de merge a `main`.
