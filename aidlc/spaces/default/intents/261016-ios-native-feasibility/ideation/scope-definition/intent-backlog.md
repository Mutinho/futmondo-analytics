# Intent Backlog — App nativa iOS (Swift) + xtool

> Backlog priorizado de proto-Units (capacidades), priorización MoSCoW alineada con el MVP y
> la secuenciación risk-first. Fuentes: `[QS<n>]`/`[QF<n>]`/`[Q<n>]`, reglas `[memory:M<n>]`.
> NO es un plan de construcción fino (eso sería un intent posterior); es el backlog de
> ideación que acompaña al scope-document.

## Priorización (MoSCoW)

| ID | Proto-Unit (capacidad) | MoSCoW | Fase | Dependencias | Source |
|----|------------------------|--------|------|--------------|--------|
| B-01 | Spike cadena `xtool` (build+firma gratuita+install en iPhone desde WSL) | Must | F0 | D-02 (WSL+Swift 6.4+usbmuxd), D-03 (Apple ID) | [QS1] [QF2] |
| B-02 | Cliente de red Swift (capa HTTP hacia `/api/v1/*`, `/auth/*`) | Must | F1 | B-01 | [QF4] |
| B-03 | Auth nativa: login + refresh token en **Keychain** | Must | F1 | B-02; D-01 (posible ajuste `/auth/refresh`) | [QS2] [QF4] [memory:M2] |
| B-04 | Pantalla Presupuesto (SwiftUI) | Must | F2 | B-02, B-03 | [QS2] [QS3] [Q6] |
| B-05 | Pantalla Mercado (SwiftUI) | Must | F2 | B-02, B-03 | [QS2] [QS3] [Q6] |
| B-06 | Pantalla Favoritos (SwiftUI) | Should | F3 | B-02, B-03 | [QS3] [Q6] |
| B-07 | Pantalla Calculadora (SwiftUI) | Should | F3 | B-02, B-03 | [QS3] [Q6] |
| B-08 | Navegación nativa (menú/tab bar iOS) entre pantallas | Must | F2 | B-03 | [Q1] [Q8] |
| B-09 | Flujo de reinstalación/refirmado de bajo esfuerzo (~7 días) | Should | F0/F1 | B-01 | [QS1] (R-02) [QF3] |
| B-10 | Exploración documentada de widget (viabilidad + idea) | Could | F-fast-follow | B-04/B-05 (datos) | [QS4] [QF2] |
| B-11 | Notificaciones push | Won't (v1) | — | Cuenta de pago | [QS4] (R-03) |

## Lectura del backlog

- **Must (MVP + base técnica)**: B-01..B-05, B-08. Es el camino crítico risk-first hasta el
  primer hito usable. [QS1] [QS2]
- **Should (completar núcleo)**: B-06, B-07, B-09. Tras el MVP. [QS3]
- **Could (exploración)**: B-10 (widgets, sólo documentar/esbozar). [QS4]
- **Won't (v1)**: B-11 (push, fuera por coste). [QS4]

## Assumptions & Open Questions

- [assumption] B-03 depende de resolver D-01 (contrato de `/auth/refresh`); si el backend ya
  admite refresh por header/body, B-03 no necesita cambios externos. [QF4]
- [assumption] El tamaño/esfuerzo de cada proto-Unit se estimará en un intent de
  construcción posterior; aquí sólo se priorizan y secuencian. [QS1]
