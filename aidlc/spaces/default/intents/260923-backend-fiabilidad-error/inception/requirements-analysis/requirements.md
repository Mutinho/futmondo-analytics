# Requirements — Fiabilidad backend (FR3.2 + FR4)

## Intent Analysis

El objetivo es endurecer la fiabilidad del backend de `futmondo-analytics`
para que los fallos no se enmascaren ni corrompan datos: hoy ~194 capturas
amplias de excepción ocultan errores, y las integraciones externas (Sofascore,
Futmondo) pueden dejar la base de datos inconsistente ante un baneo o una
entrada fallida. La meta no es una reescritura sino una intervención acotada y
aditiva que distinga error recuperable de fatal, tipifique y propague los modos
de fallo de integración, y refleje el fallo en el estado sin corromper datos. [desc][Q(intent-capture)]

## Functional Requirements

### FR3.2 — Manejo de errores (taxonomía recuperable/fatal)

- **FR3.2.1** — El sistema DEBE distinguir error **recuperable** de **fatal**:
  recuperable → el paso se marca `DEGRADED` (vía `sync_step_status.py`) y la
  operación continúa; fatal → aborta limpio, sin dejar datos a medias. [desc]
- **FR3.2.2** — La primera oleada de reducción de broad-except cubre: arranque
  (`main.py`), migraciones (`scripts/migrate_*`) y la capa de conexión de BD
  (`db_connection.py`); cada captura restante queda justificada como recuperable
  o fatal. [scope]
- **FR3.2.3** — La regla `E722` (bare-except) se re-habilita como **advisory**
  por trinquete en `backend/ruff.toml` (quitada del `ignore`), sin promover
  `ruff check` a bloqueante, en un commit aislado sin `ruff format`. [memory:M2]

### FR4 — Contratos y robustez de integraciones externas

- **FR4.1** — Las excepciones de integración viven en un módulo estrecho y
  testeable `integration_errors` con una raíz común `IntegrationError`, del que
  heredan los subtipos por modo de fallo de Sofascore y Futmondo (nombres
  exactos = functional-design). [memory:M2]
- **FR4.2** — `futmondo_client` DEBE dejar de tragar excepciones y devolver
  `None` como señal de fallo; pasa a excepciones tipadas por modo de fallo
  (timeout, respuesta heterogénea/no parseable, baneo), propagadas, con
  `except <Typed>: raise` antes del `except Exception` genérico. [desc]
- **FR4.3** — Antes del cambio de contrato de `_make_request`, se entrega un
  **inventario verificable de llamadores** y se caracteriza su comportamiento
  actual; la migración cubre el núcleo (`_make_request` + los llamadores donde
  un `None` no detectado corrompe datos); el resto queda como deuda. [memory:M1][desc]
- **FR4.4** — Ante baneo (Sofascore 403) o entrada fallida (Futmondo), el
  sistema DEBE **detectar** el fallo y **reflejarlo en el estado** del sync
  (`DEGRADED`/fallido), sin escribir datos parciales corruptos. [desc]
- **FR4.5** — Se documentan los **contratos y modos de fallo esperados** de
  Sofascore (API no oficial vía `curl_cffi`, baneo de IP 403) y Futmondo
  (endpoints heterogéneos, login, getters). [desc]

## Non-Functional Requirements

- **NFR1 — Observabilidad (logging estructurado)**: cada fallo de integración
  (recuperable o fatal) emite un **log estructurado** con modo de fallo +
  contexto no sensible (`sync_step`, `reason`, status, endpoint, `task_id`),
  para que `fly logs` + `grep` sirvan de observabilidad a coste 0 €. Nunca
  incluye material de credencial. [Q1]
- **NFR2 — No-corrupción de datos (verificable)**: ante fallo fatal en un punto
  de escritura (p. ej. el `DELETE FROM team_prizes ... NOT IN (...)`), la
  tabla/caché queda en estado consistente (todo-o-nada), no a medias; criterio
  de aceptación = un spec fuerza el fallo en el punto de escritura y asvera el
  estado resultante. [Q3][memory:M1]
- **NFR3 — Seguridad (sin secretos en excepciones)**: ninguna excepción de
  integración incluye password/token del usuario en su mensaje, `repr` o
  `exc_info`. [practices Q5]
- **NFR4 — Sin regresión**: la suite `pytest` existente permanece en verde; el
  gate CI bloqueante (gitleaks + `pytest` + `ng test`) pasa antes de fusionar a
  `main`. [desc]
- **NFR5 — Coste 0 €**: sin dependencias de pago; la stdlib basta (cualquier
  librería nueva sería OSS y fijada a versión). [memory][desc]

## Constraints

- Stack fijo (FastAPI/Python 3.12, Neon, Fly.io); sin cambios de
  infraestructura. [desc]
- NO ampliar los god-files (`data_sync_service.py`, `data_manager_v2.py`) ni el
  patrón SQL-en-router; código nuevo tras una capa/función estrecha testeable. [memory:M... ][desc]
- Characterization-first antes de endurecer cada captura y antes del cambio de
  contrato de `_make_request`. [memory:M1]
- Specs significativas que aseveran el efecto; nada de `pytest.raises` sin
  aserción de estado. [memory:M1]
- Sin reintentos/backoff en este intent (recuperable = detectar + degradar). [Q2]

## Assumptions

- FR3.1 (`sync_step_status.py`, `StepStatus.DEGRADED`) está entregado y es
  reusable como anclaje de estado (verificado en código). [feasibility A-1]
- FR2 (reemplazo transaccional atómico) está entregado y sirve de patrón de
  referencia para la no-corrupción. [desc]

## Out of Scope

- Las 29 capturas completas de `data_sync_service.py`, salvo los puntos de
  corrupción de datos concretos. [scope]
- Los `except: pass` de `data_manager_v2.py` y `photo_service.py` (deuda; god-file → Intent 3). [practices Q6]
- El resto de broad-except del backend fuera de la primera oleada. [scope]
- Poda de configuración muerta (Turso/SQLite) → Intent 2. [scope]
- Descomposición de god-files → Intent 3. [scope]
- Retry/backoff de fallos recuperables. [Q2]
- Cierre de la asimetría de cobertura backend (`--cov` en `verify`) → deuda diferida. [memory]

## Open Questions

- Los nombres y subtipos exactos de la jerarquía `IntegrationError` se deciden
  en functional-design. [memory:M2]
- El conjunto exacto de llamadores de `_make_request` a migrar (núcleo vs deuda)
  se fija con el inventario verificable en construcción. [FR4.3]

## Assumptions & Open Questions

None.
