# Units of Work — Fiabilidad backend (FR3.2 + FR4)

Dos unidades por eje de dependencia. Organización del trabajo (no despliegue
independiente): todo va en `futmondo-api`. Orden dependencia-primero. [Q1][Q3]

## Tabla de unidades

| Unit ID | Directory | Nombre | Kind | Complejidad | Depende de |
|---|---|---|---|---|---|
| U1 | u1-error-layer | Capa de errores | library | M | — |
| U2 | u2-integrations | Integraciones | service | M/L | U1 |

## U1 — `u1-error-layer` (capa de errores)

- **Descripción**: la base de manejo de errores del intent. Crea el módulo
  `IntegrationErrors` (raíz común `IntegrationError` + subtipos por modo de
  fallo: baneo, timeout, respuesta no parseable) y endurece las capturas amplias
  de la primera oleada distinguiendo recuperable de fatal.
- **Boundaries**: componente nuevo `IntegrationErrors`; endurecimiento de
  capturas en `main.py` (arranque), `scripts/migrate_*` (migraciones) y
  `db_connection.py`. NO amplía god-files. [memory]
- **Responsabilidades**: declarar la jerarquía de excepciones; clasificar
  recuperable/fatal en arranque/migraciones/conexión.
- **Requisitos**: FR3.2.1, FR3.2.2, FR3.2.3, FR4.1, NFR3.
- **Deployment**: embedded en `futmondo-api`.
- **Notas**: characterization-first antes de endurecer cada captura; specs que
  aseveran el efecto; `E722` re-habilitado advisory en commit aislado.

## U2 — `u2-integrations` (integraciones)

- **Descripción**: los clientes externos y la ruta de sync se apoyan en la capa
  de errores de U1. `FutmondoClient` deja de tragar a `None` y lanza tipadas;
  `SofascoreClient` alinea sus excepciones a la raíz común; la ruta de sync
  detecta baneo/entrada fallida y lo refleja en estado (`DEGRADED`) sin corromper
  datos; se entrega el inventario verificable de llamadores de `_make_request`.
- **Boundaries**: `FutmondoClient`, `SofascoreClient`, punto de captura de la
  ruta de sync (`SyncService`, solo endureciendo), reuso de `SyncStepStatus`;
  no-corrupción en el punto `team_prizes` con reemplazo transaccional atómico.
- **Responsabilidades**: señalar el fallo de integración como excepción tipada;
  traducir recuperable→`DEGRADED` / fatal→abortar-limpio; logging estructurado.
- **Requisitos**: FR4.2, FR4.3, FR4.4, FR4.5, NFR1, NFR2.
- **Deployment**: embedded en `futmondo-api`.
- **Notas**: caracterizar el contrato de `_make_request` y entregar el inventario
  de llamadores ANTES de migrar; migrar núcleo (`_make_request` + llamadores que
  corrompen datos), resto deuda; sin retry/backoff.

## Assumptions & Open Questions

None.
