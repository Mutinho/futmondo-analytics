# Initiative Brief — Fiabilidad backend (FR3.2 + FR4)

## Intent y problema

Endurecer la fiabilidad del backend de `futmondo-analytics`: ~194 capturas
amplias de excepción (7 bare + 187 `except Exception`) enmascaran fallos
silenciosos y pueden corromper datos ante un baneo/entrada fallida de una
integración externa. El intent cubre **FR3.2** (manejo de errores, taxonomía
recuperable/fatal) y **FR4** (contratos y detección de fallo de Sofascore y
Futmondo reflejada en el estado, sin corromper datos). [desc][Q1]

## Validación de mercado

No aplica: intent de fiabilidad interna sobre sistema brownfield en producción
(market-research omitida con justificación). [desc]

## Viabilidad y riesgos

Viable, riesgo bajo-medio, sin dependencias nuevas (stdlib), sin cambios de
infraestructura, coste 0 €. Riesgos principales (RAID), todos con mitigación:
regresión al endurecer capturas (characterization-first + gate CI), baneo real
en pruebas (dobles/mocks), clasificación errónea recuperable/fatal (diseño
explícito), desbordamiento hacia god-file (frontera + guardarraíl). [Q2]

## Frontera de alcance

- **In**: FR3.2 primera oleada (taxonomía + arranque/migraciones/`db_connection.py`)
  y FR4 (Futmondo tipado + detección de baneo en estado + doc de contratos). [Q1]
- **Out (deuda)**: 29 capturas completas de `data_sync_service.py` (salvo
  corrupción), resto de broad-except, poda (Intent 2), god-files (Intent 3). [Q1]

## Visuales de concepto

No aplica: intent backend-only, sin UI nueva (rough-mockups omitida). [desc]

## Plan de equipo

Mantenedor único, coste 0 €; sin composición de equipo ni mob (team-formation
omitida con justificación). El compromiso es el propio tiempo del mantenedor. [Q3]

## Recomendación go/no-go

**GO** — proceder a Inception (reverse-engineering del backend brownfield →
requisitos). La iniciativa es viable, acotada, con riesgos mitigados y valor
claro (fiabilidad y no-corrupción de datos). [Q4]

## Assumptions & Open Questions

None.
