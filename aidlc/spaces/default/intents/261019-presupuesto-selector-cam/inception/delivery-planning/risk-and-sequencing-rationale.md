# Risk & Sequencing Rationale — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (delivery-planning). Idioma: castellano; tokens técnicos verbatim en inglés.

## Por qué este orden

- **Bolt 1 (datos/lógica) primero**: es la base testeable (`swift test`) sobre la que se apoya la UI; permite validar formato de dinero, orden, fallback de endpoints y persistencia antes de pintar nada. Reduce el riesgo de rehacer la vista.
- **Bolt 2 (UI) después**: consume contratos ya verificados de Bolt 1; su riesgo (descubribilidad del selector, fidelidad visual, 60 fps) se valida en dispositivo al final.

## Riesgos y mitigaciones (del RAID)

| Riesgo | Mitigación en el plan |
|--------|-----------------------|
| R-01 descubribilidad del selector en navigation bar | Se materializa en Bolt 2; validación en dispositivo; patrón revisable en follow-up si incomoda. |
| R-02 formateo de dinero M/K | Caracterizado como `MoneyFormatter` testeable en Bolt 1 (tabla de casos). |
| R-03 validación de UI depende de iPhone 13 Pro + `xtool` | Asumido; verificación manual como en F1, al cierre de Bolt 2. |

## Walking skeleton

OFF (team practice): no hay componente nuevo que arrancar de cero; el backend y el pipeline están en producción.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/feasibility/raid-log.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/delivery-planning/bolt-plan.md`

## Assumptions & Open Questions

None.
