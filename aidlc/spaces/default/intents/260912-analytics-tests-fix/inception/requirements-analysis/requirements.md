# Requisitos — Arreglo de tests de AnalyticsService

## Sources

- [desc] Initial description: "Arreglar los 3 tests preexistentes en verde en backend/tests/test_analytics_service.py: AnalyticsService no tiene atributo _team_cache (test_championship_trends, test_clause_network) y falta la clave latest_price (test_player_value_trend). Objetivo: dejar la suite completa de pytest en verde para desbloquear el gate de CI de fly-deploy.yml." (`project-description.json`)
- [scope] Workflow-selected scope: `bugfix` (Depth Minimal, Test Strategy Minimal).
- [Q1] Estrategia de arreglo elegida: en el TEST (Alternativa A) — respuesta guiada del usuario.
- [Q2] Alcance de verificación elegido: toda la suite de pytest del backend en verde — respuesta guiada del usuario.
- Reverse Engineering (brownfield): `codekb/futmondo-analytics/code-quality-assessment.md` (diagnóstico de los 3 fallos, ADR-RE-001), `business-overview.md`, `architecture.md`.

## Análisis de intención

El usuario quiere restaurar la red de seguridad de la capa analítica: la suite
de caracterización de `AnalyticsService` debe volver a verde para que el gate de
CI `verify` de `fly-deploy.yml` (que ejecuta pytest) deje de bloquear los
despliegues a producción. El objetivo real no es "cambiar comportamiento" sino
**recuperar la fiabilidad de los tests** con el menor impacto posible sobre el
código de producción, alineado con el scope `bugfix`.

Reverse Engineering identificó dos causas independientes de los 3 fallos:
1. El fixture `analytics_service` monkeypatchea `AnalyticsService.__init__` con
   un `fake_init` que solo asigna `self.dm` y omite `self._team_cache` y
   `self._player_cache` (presentes en el `__init__` real,
   `analytics_service.py:16-17`) → `AttributeError`.
2. `get_player_value_trend` emite la clave `last_transaction_price`
   (`analytics_service.py:474`) mientras el test exige `latest_price` → `KeyError`.

Decisión del usuario (Q1): arreglar en el **test**, sin tocar el servicio ni su
contrato de salida (`/api/v1/analytics/*` no se ve afectado).

## Requisitos funcionales

### FR1 — Restaurar el estado de instancia bajo el fixture de test
- **FR1.1**: El fixture `analytics_service` de `backend/tests/test_analytics_service.py` DEBE inicializar `self._team_cache = {}` y `self._player_cache = {}` en su `fake_init`, replicando el estado del `__init__` real sin instanciar `DataManagerV2`.
- **FR1.2**: Tras FR1.1, `test_championship_trends` DEBE pasar (la cadena `get_championship_trends` → `_safe_team_info` deja de lanzar `AttributeError`).
- **FR1.3**: Tras FR1.1, `test_clause_network` DEBE pasar (la cadena `get_clause_network` → `_resolve_team` → `_build_team_lookup` deja de lanzar `AttributeError`).

### FR2 — Alinear la aserción de clave con el contrato real del servicio
- **FR2.1**: `test_player_value_trend` DEBE afirmar sobre la clave real emitida por el servicio, `last_transaction_price`, en lugar de `latest_price`, conservando el valor esperado (`1000000`).
- **FR2.2**: El código de producción `analytics_service.py` NO se modifica; la clave de salida `last_transaction_price` permanece intacta y el contrato consumido por `/api/v1/analytics/*` no cambia.
- **FR2.3**: Tras FR2.1 (y FR1.1 para el acceso a `_player_cache` vía `_safe_player_info`), `test_player_value_trend` DEBE pasar.

### FR3 — Preservar el resto de la suite
- **FR3.1**: Los otros 3 tests del mismo fichero (`test_player_form`, `test_opportunity_streaks`, `test_matchday_projections`) DEBEN seguir en verde.
- **FR3.2**: El resto de ficheros de caracterización del backend (`test_auth_characterization.py`, `test_db_admin_guard.py`, `test_jwt_startup.py`, `test_db_engine_characterization.py`, `test_finance_characterization.py`) DEBEN seguir en verde.

## Requisitos no funcionales

- **NFR1** (Fiabilidad): tras el arreglo, la ejecución completa de `pytest` desde `backend/` DEBE terminar con 0 fallos y 0 errores (criterio pass/fail: exit code 0 de pytest).
- **NFR2** (Mínimo blast radius): el cambio DEBE limitarse a `backend/tests/test_analytics_service.py`; ningún fichero bajo `backend/app/` se modifica (verificable por diff).
- **NFR3** (Mantenibilidad / no falsos verdes): las aserciones modificadas DEBEN seguir comprobando valores reales derivados de los stubs; no se permite debilitar un test a `assert True` ni eliminar aserciones para forzar el verde (org.md Testing Standards).

## Restricciones

- **C1**: Scope `bugfix` — postura de test = regresión dirigida al bug + suite existente en verde; no se introduce nueva metodología ni piso de cobertura adicional.
- **C2**: Regla de proyecto coste 0€ — no se añaden dependencias con gasto recurrente (`project.md`).
- **C3**: El contrato de salida de `AnalyticsService` (nombres de clave del dict) es consumido por endpoints `/api/v1/analytics/*` no re-verificados en profundidad; por eso NO se renombra en el servicio (decisión Q1=A).

## Assumptions & Open Questions

- [assumption] El stub `get_transactions_raw` del fixture alimenta `price: 1000000`, por lo que `last_transaction_price` == `1000000` es el valor correcto a afirmar en FR2.1. (Confirmado por el escaneo de RE; sujeto a re-verificación en `build-and-test` al ejecutar la suite real.)
- [assumption] El entorno de build (stage `build-and-test`) dispone de `pytest` instalado; el diagnóstico de RE fue estático porque el entorno de análisis no lo tenía. La ejecución real y su verde se validan en `build-and-test`.

## Out of scope

- Renombrar la clave `last_transaction_price` → `latest_price` en el servicio (Alternativa B) y la revisión de consumidores `/api/v1/analytics/*` asociada.
- Refactor de la deuda técnica adyacente detectada en RE (mezcla de caches en `_safe_team_info`, `try/except` amplio en `_build_team_lookup`, god files).
- Cualquier cambio en el frontend Angular o en su suite de tests (`ng test`).
- Corrección de otros hallazgos de RE no relacionados con los 3 tests (sesiones in-memory, config heredada, etc.).
