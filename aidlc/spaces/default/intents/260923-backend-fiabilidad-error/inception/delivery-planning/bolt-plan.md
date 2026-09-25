# Bolt Plan — Fiabilidad backend (FR3.2 + FR4)

Un **Bolt** es una pasada de construcción sobre una pieza de trabajo que acaba
en algo que corre (aquí: código + tests en verde, mergeable). Dos Bolts, en
serie, en orden de dependencia. **Walking skeleton OFF** (el sistema ya está en
producción; no hay nada que arrancar de cero). [memory:M1]

## Bolt 1 — U1 `u1-error-layer` (capa de errores)

- **Unidades**: U1.
- **Walking skeleton**: no.
- **Definition of Done**: módulo `IntegrationErrors` creado (raíz + subtipos);
  capturas amplias de arranque (`main.py`), migraciones (`scripts/migrate_*`) y
  `db_connection.py` endurecidas con taxonomía recuperable/fatal;
  characterization-first en cada captura tocada; specs que aseveran el efecto;
  `E722` re-habilitado advisory en commit aislado; suite `pytest` en verde; gate
  CI (gitleaks + pytest + ng test) pasa.
- **Confidence hypothesis**: la base de excepciones tipadas y la clasificación
  recuperable/fatal funcionan sin romper el comportamiento actual (sin regresión
  en la suite existente).
- **Demo**: los tests de la capa de errores en verde, `ruff check` reportando
  bare-except, y la suite existente intacta.

## Bolt 2 — U2 `u2-integrations` (integraciones)

- **Unidades**: U2 (depende de U1).
- **Walking skeleton**: no.
- **Definition of Done**: inventario verificable de llamadores de `_make_request`
  entregado; `FutmondoClient` lanza excepciones tipadas propagadas (fin del
  `return None`); `SofascoreClient` alineado a la raíz común; detección de
  baneo/entrada fallida reflejada en estado (`DEGRADED`) sin corromper datos;
  no-corrupción en el punto `team_prizes` (reemplazo transaccional atómico, spec
  que fuerza el fallo y asvera estado todo-o-nada); logging estructurado (NFR1);
  doc de contratos (FR4.5); specs que aseveran el efecto; suite en verde; gate CI
  pasa. Empieza por lo de mayor riesgo (corrupción de datos).
- **Confidence hypothesis**: ante un baneo/entrada fallida (simulado con dobles),
  el sync marca el paso `degraded`/fallido y NO deja datos a medias; el cambio de
  contrato no rompe a los llamadores del núcleo.
- **Demo**: specs de modo de fallo (recuperable→`DEGRADED`, fatal→propaga sin
  datos a medias) en verde; inventario de llamadores; doc de contratos.

## Secuencia

`Bolt 1 (U1)` → `Bolt 2 (U2)`. En serie. Sin paralelismo (mantenedor único,
dependencia U2→U1). Iteración de construcción: **unit-major**.

## Assumptions & Open Questions

None.
