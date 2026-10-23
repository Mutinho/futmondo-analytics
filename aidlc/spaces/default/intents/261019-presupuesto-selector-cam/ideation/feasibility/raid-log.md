# RAID Log — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (feasibility). Idioma: castellano; tokens técnicos verbatim en inglés.
> RAID = Risks, Assumptions, Issues, Dependencies.

## Risks

| ID | Riesgo | Prob. | Impacto | Mitigación |
|----|--------|-------|---------|------------|
| R-01 | El patrón del selector en navigation bar resulta poco descubrible o incómodo con muchos campeonatos. | Media | Medio | Validar en dispositivo; si molesta, revisar patrón (sheet/picker) en un follow-up. |
| R-02 | La lógica de formateo de dinero (M/K con signo) no reproduce fielmente el `money` pipe. | Baja | Bajo | Caracterizar el formateo como lógica pura testeable en `FutmondoKit`. |
| R-03 | La validación de UI en dispositivo depende del iPhone 13 Pro + arnés `xtool` (arrastrado de F1). | Media | Bajo | Asumido; verificación manual como en F1. |

## Assumptions

| ID | Supuesto |
|----|----------|
| A-01 | Los endpoints existentes devuelven los datos suficientes para la vista sin cambios de backend. |
| A-02 | El formato de dinero sigue el patrón de la web (M/K abreviado). |
| A-03 | La librería de diseño de F1 cubre los tokens/componentes necesarios; si falta alguno, se amplía dentro del mismo estilo. |

## Issues

| ID | Issue |
|----|-------|
| I-01 | Ninguno abierto al inicio del intent. |

## Dependencies

| ID | Dependencia |
|----|-------------|
| D-01 | `FutmondoKit`/`FutmondoApp` DesignSystem de F1 (red, auth, tokens de diseño). |
| D-02 | Endpoints del backend existente (`balances`, `championships`). |
| D-03 | Tema Angular (`styles.scss` + vista `budget-overview`) como fuente de verdad. |

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/feasibility/feasibility-assessment.md`.
- [memory:M1] reglas durables de `project.md`/`team.md`.

## Assumptions & Open Questions

None.
