# Contract Summary — Fiabilidad backend (FR3.2 + FR4)

Contratos que el sistema debe honrar. Un contrato de código intra-proceso
(frontera U1↔U2) y dos contratos de fallo asumidos de APIs de terceros
(Sofascore, Futmondo). Sin API pública nueva expuesta por este intent.

## Tabla de contratos

| # | Provider Unit | Consumer | Mechanism | Owner |
|---|---|---|---|---|
| 1 | U1 `u1-error-layer` (IntegrationErrors) | U2 `u2-integrations` (clientes + ruta de sync) | shared code (jerarquía de excepciones) | U1 |
| 2 | External: Sofascore API | U2 `SofascoreClient` | contrato de fallo asumido (HTTP) | — (tercero) |
| 3 | External: Futmondo API | U2 `FutmondoClient` | contrato de fallo asumido (HTTP) | — (tercero) |

## Contrato 1 — Frontera U1↔U2: jerarquía `IntegrationError` (shared code)

Contrato de código compartido: U1 define los tipos, U2 los lanza, la ruta de
sync los captura. El **tipo** codifica la clasificación recuperable/fatal.

```yaml
# shared-schema (Python exception hierarchy) — contrato de código, no de red
IntegrationError:            # raíz común; la ruta de sync captura por la raíz
  base: Exception
  invariants:
    - "el mensaje/repr/exc_info NUNCA incluye password ni token (NFR3)"
    - "lleva contexto NO sensible: failure_mode, status?, endpoint?"
  attributes:
    failure_mode: "enum: ban | timeout | unparseable | <otro>"
    status: "int? (código HTTP si aplica)"
    endpoint: "str? (ruta/endpoint no sensible)"
  subtypes:
    # nombres/subtipos exactos = decisión de functional-design; forma acordada aquí
    - name: "<Ban>Error"          # p. ej. baneo 403 (fatal) — extiende SofascoreIPBanError existente
      classification: fatal
    - name: "<Timeout>Error"      # timeout puntual (recuperable)
      classification: recoverable
    - name: "<Unparseable>Error"  # respuesta heterogénea/no parseable (recuperable)
      classification: recoverable
  contract:
    provider: "U1 (integration_errors)"
    consumer: "U2 (SofascoreClient, FutmondoClient lanzan; SyncService captura)"
    guarantee: "except <Typed>: raise ANTES del except Exception genérico; nunca return None silencioso"
```

## Contrato 2 — Sofascore API (contrato de fallo asumido)

```yaml
# contrato de fallo asumido de un tercero (API no oficial vía curl_cffi)
provider: "Sofascore (externo, no controlado)"
consumer: "U2 SofascoreClient"
expected_responses:
  - status: 200
    meaning: "datos válidos"
  - status: 403
    meaning: "baneo de IP → SofascoreIpBan (FATAL): excepción tipada propagada (FR2.1 ya presente)"
  - status: 404
    meaning: "recurso ausente → None/sin datos, no fatal"
failure_handling:
  preventive: "rate-limiting en el cliente para no provocar baneo"
  ban_403: "fatal: propagar excepción tipada; NO seguir escribiendo"
  timeout_or_unparseable: "recuperable: degradar el paso (DEGRADED) y continuar"
```

## Contrato 3 — Futmondo API (contrato de fallo asumido)

```yaml
# contrato de fallo asumido de un tercero (endpoints heterogéneos)
provider: "Futmondo (externo, no controlado)"
consumer: "U2 FutmondoClient"
surface:
  - "login (credenciales de usuario) — NUNCA loguear/propagar password/token (NFR3)"
  - "getters heterogéneos (campeonato, transacciones, plantillas)"
current_antipattern: "hoy traga Timeout/RequestException/JSONDecodeError y devuelve None (a corregir, FR4.2)"
failure_handling:
  timeout: "recuperable: excepción tipada propagada; degradar y continuar"
  request_exception: "recuperable salvo que corrompa datos aguas abajo"
  json_decode_error: "recuperable (respuesta no parseable): excepción tipada"
  write_point_failure: "fatal en el punto de corrupción (p. ej. team_prizes): abortar limpio, sin datos a medias (NFR2)"
migration_note: "cambio de contrato de _make_request con inventario de llamadores previo (FR4.3); migrar núcleo, resto deuda"
```

## Reglas de propiedad del contrato

- **Contrato 1** (interno): lo posee U1. Los cambios son **aditivos** (nuevos
  subtipos heredan de `IntegrationError`; los consumidores capturan la raíz), sin
  versionado formal (mismo proceso/despliegue). Un cambio rompedor solo sería
  cambiar la raíz o eliminar un subtipo en uso.
- **Contratos 2/3** (externos): no los controlamos; documentamos el **contrato de
  fallo asumido**. Si el tercero cambia su comportamiento, se actualiza aquí y se
  ajusta la detección.

## Open questions

| Contract | Question | Blocks |
|---|---|---|
| 1 | Nombres/subtipos exactos de la jerarquía | functional-design (no bloquea la forma acordada) |
| 3 | Conjunto exacto de llamadores de `_make_request` a migrar | construcción (se fija con el inventario, FR4.3) |

## Assumptions & Open Questions

None.
