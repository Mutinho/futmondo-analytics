# Competitive Analysis — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (market-research). Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA en sentido clásico.** F2 es una **feature de paridad funcional** sobre un producto propio ya existente (Futmondo Analytics): reproduce en SwiftUI nativo la pantalla de Presupuesto que ya existe en el frontend Angular, para uso del propietario/único usuario. No hay un mercado externo que conquistar, ni usuarios a captar, ni competidores a desplazar: es trabajo interno de portabilidad de UI.

## Referencia real (no competidores, sino fuente de verdad)

| Referencia | Qué aporta |
|------------|------------|
| Web Futmondo Analytics (`angular-app`, vista Presupuesto) | **Fuente de verdad funcional y visual** que F2 reproduce (no un competidor). |
| App oficial de Futmondo | Antecedente del dominio (fantasy football); F2 no compite, complementa el análisis que la web ya ofrece. |
| Apple HIG | Referencia de patrones nativos (navigation bar, menús, listas) donde Material 3 no mapea 1:1. |

Conclusión: no hay análisis competitivo que mueva decisiones de este intent; la única "referencia" relevante es la propia web como fuente de verdad.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/intent-capture/intent-statement.md` — alcance de paridad funcional.
- [memory:M1] `project.md`/`team.md`: producto propio, single-maintainer, coste 0 €.

## Assumptions & Open Questions

None.
