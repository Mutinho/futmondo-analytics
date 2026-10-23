# User Stories Assessment — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (user-stories). Idioma: castellano; tokens técnicos verbatim en inglés.

## Cobertura e independencia

| US | MoSCoW | Independiente | Testeable | Cubre FR |
|----|--------|---------------|-----------|----------|
| US1 Ver presupuesto | Must | Sí (con un campeonato activo) | Sí (AC verificables) | FR1, FR4 |
| US2 Cambiar campeonato | Must | Sí | Sí | FR3 |
| US3 Ordenar | Should | Sí (sobre US1) | Sí | FR2 |
| US4 Navegación base | Must | Sí | Sí (arranque en pestaña) | FR5 |

- Todas las historias son independientemente testeables; US3 opera sobre la lista de US1 pero no la bloquea (orden por defecto por saldo).
- Sin contradicciones entre historias ni con los requisitos.
- Valor de negocio claro por historia (control de presupuesto, movilidad entre campeonatos, comparación, sensación nativa).

## Riesgos

- US2: descubribilidad del selector en navigation bar (riesgo R-01 del RAID); se valida en dispositivo.
- US4: dependencia del material Liquid Glass del SDK (coste 0 €, automático); sin riesgo de dependencia de pago.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/user-stories/stories.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/feasibility/raid-log.md`

## Assumptions & Open Questions

None.
