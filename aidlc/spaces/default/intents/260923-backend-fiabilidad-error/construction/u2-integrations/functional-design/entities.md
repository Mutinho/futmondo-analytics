# Entities — u2-integrations (Integraciones)

Este intent es de **fiabilidad** (comportamiento de error/estado), no de datos.
No introduce entidades de dominio nuevas: campeonato, transacciones y premios
conservan su forma y su dueño (ver `domain-design/components.md` → Entity
Ownership). Lo que U2 sí modela es la **jerarquía de excepciones de
integración** que define U1 y consumen los clientes/la ruta de sync, más el
**contexto no sensible** que cada excepción transporta. Se documenta aquí como
modelo estructural porque es el contrato de tipos que atraviesa la frontera
U1↔U2 y gobierna la traducción recuperable/fatal (FR4.1, FR4.2, NFR3).

## Part A — Source of truth (machine-readable)

```yaml
# No hay entidades de dominio persistentes nuevas en U2.
domain_entities: []

# Modelo estructural: jerarquía de excepciones de integración (contrato de código,
# raíz en U1 `integration_errors`, lanzada por U2, capturada por SyncService).
exception_model:
  - name: IntegrationError
    kind: exception-root
    description: >
      Raíz común de todos los fallos de integración externa. SyncService captura
      por esta raíz como último except tipado antes del `except Exception`
      genérico. No se lanza directamente; se lanzan sus subtipos.
    base: Exception
    attributes:
      - name: failure_mode
        type: enum(ban, timeout, unparseable, request_exception, other)
        required: true
        description: >
          modo de fallo; redundante con el subtipo, útil para logging estructurado
          (NFR1). El enum es abierto por diseño (`other` cubre modos no previstos),
          honrando el `<otro>` del Contrato 1.
      - name: status
        type: int
        required: false
        description: código HTTP si aplica (p. ej. 403)
      - name: endpoint
        type: string
        required: false
        description: ruta/endpoint NO sensible (nunca credenciales)
    constraints:
      - id: EC-NFR3
        rule: >
          Ni el mensaje, ni `__str__`/`repr`, ni `exc_info` incluyen password ni
          token del usuario. Sólo modo de fallo + contexto no sensible.
    classification: n/a  # la clasificación por defecto vive en los subtipos; el punto de escritura puede elevar a fatal (ver EC-CTX)

  - name: IntegrationBanError
    kind: exception-subtype
    description: baneo del proveedor (p. ej. Sofascore 403). Fallo terminal para el paso.
    base: IntegrationError
    classification: fatal
    attributes:
      - name: status
        type: int
        required: false
        description: normalmente 403
    notes: >
      `SofascoreIPBanError` (existente, FR2.1) se re-parenta para heredar de
      IntegrationBanError; conserva su nombre y sus captores actuales, y queda
      cubierto por `except IntegrationError`.

  - name: IntegrationTimeoutError
    kind: exception-subtype
    description: timeout puntual al contactar el proveedor.
    base: IntegrationError
    classification: recoverable

  - name: IntegrationUnparseableError
    kind: exception-subtype
    description: respuesta heterogénea o no parseable (p. ej. JSON inválido).
    base: IntegrationError
    classification: recoverable

  - name: IntegrationRequestError
    kind: exception-subtype
    description: >
      error de conexión/petición HTTP no clasificable como timeout, baneo o
      respuesta no parseable (el `requests.RequestException` que hoy se traga como
      None). Cubre el modo `request_exception` del Contrato 3.
    base: IntegrationError
    classification: context-dependent
    notes: >
      Recuperable por defecto (degradar y continuar), PERO fatal cuando ocurre en
      un punto de escritura que podría corromper datos (Contrato 3:
      "recuperable salvo que corrompa datos aguas abajo"). Ver EC-CTX.

entity_constraints:
  - id: EC-CTX
    rule: >
      La clasificación recuperable/fatal es por defecto la del subtipo, PERO un
      fallo de integración que alcanza un punto de escritura que podría dejar
      datos a medias se trata como FATAL con independencia de su subtipo por
      defecto (aborta limpio, sin datos parciales). Esto cubre el matiz del
      Contrato 3 (`request_exception` recuperable salvo que corrompa datos;
      `write_point_failure` fatal). La elevación a fatal la decide el punto de
      captura por su contexto (ver rules.md BR2.3 y functional-spec §1/§3), no un
      atributo del tipo.

relationships:
  - from: SofascoreClient
    to: IntegrationError
    cardinality: raises
    note: lanza IntegrationBanError (403) e Integration{Timeout,Unparseable}Error
  - from: FutmondoClient
    to: IntegrationError
    cardinality: raises
    note: lanza subtipos tipados en vez de devolver None (FR4.2)
  - from: SyncService
    to: IntegrationError
    cardinality: catches
    note: captura fatal primero, recuperable después, antes del `except Exception`
```

## Part B — Vista humana

**No hay entidades de dominio nuevas.** El único modelo estructural que U2
formaliza es la jerarquía de excepciones (definida en U1, consumida en U2):

| Tipo | Base | Clasificación | Modo de fallo | Notas |
|---|---|---|---|---|
| `IntegrationError` | `Exception` | — (raíz) | — | raíz común; capturada por `SyncService`; invariante NFR3 |
| `IntegrationBanError` | `IntegrationError` | fatal | baneo (403) | `SofascoreIPBanError` se re-parenta bajo este |
| `IntegrationTimeoutError` | `IntegrationError` | recuperable | timeout | — |
| `IntegrationUnparseableError` | `IntegrationError` | recuperable | respuesta no parseable | — |
| `IntegrationRequestError` | `IntegrationError` | context-dependent | `request_exception` | recuperable por defecto; **fatal en punto de escritura** (EC-CTX) |

**Clasificación (EC-CTX):** la clasificación por defecto la da el subtipo, pero
un fallo de integración que alcanza un punto de escritura que podría corromper
datos se eleva a **fatal** en el punto de captura (Contrato 3), con
independencia del subtipo. Esto cubre `request_exception` (recuperable salvo que
corrompa datos) y `write_point_failure` (fatal).

**Contexto que transporta cada excepción (NFR1/NFR3):** `failure_mode`,
`status?`, `endpoint?` — nunca password ni token.

Las entidades de dominio persistentes (campeonato, transacciones, `team_prizes`)
**no cambian de forma ni de dueño**; U2 sólo endurece el comportamiento de fallo
y la integridad transaccional del punto de escritura `team_prizes` (ver
`rules.md` BR4/BR5 y `functional-spec.md`).
