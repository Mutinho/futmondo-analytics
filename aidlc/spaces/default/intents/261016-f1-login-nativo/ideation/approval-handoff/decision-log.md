# Decision Log — F1: Login nativo end-to-end (ideación)

> Decisiones consolidadas de la fase de ideación. Idioma: castellano; tokens técnicos verbatim
> en inglés.

| # | Decisión | Etapa | Fundamento |
|---|----------|-------|------------|
| 1 | F1 agrupa B-02 (cliente de red Swift) + B-03 (auth nativa con refresh token en Keychain). | intent-capture | Backlog del intent de viabilidad; camino risk-first tras F0. |
| 2 | D-01 (ajuste del backend) es **aditivo** por body/header, dejando intacto el canal cookie `HttpOnly` de la PWA. | intent-capture (Q1=A) | Verificado en `auth/routes.py`; evita regresión de la PWA. |
| 3 | Cliente de red auth-first + una llamada de humo a `/api/v1/user/me`. | intent-capture (Q2=A) | Alcance mínimo verificable; el resto llega con las pantallas (F2). |
| 4 | Access token en memoria + refresh token en Keychain + refresh automático (un reintento ante 401). | intent-capture (Q3=A) | Espeja la PWA; regla durable de credenciales nunca en claro. |
| 5 | El ajuste de backend completo (login/refresh/logout + tests) entra en F1. | intent-capture (Q4=A) | F1 queda end-to-end verificable. |
| 6 | Definición de hecho: `pytest` verde + gate de CI + validación manual en iPhone 13 Pro. | intent-capture (Q5=A) | Sin arnés de test nativo todavía (deuda registrada). |
| 7 | Market Research **saltada**. | market-research (SKIP) | Mercado/build-vs-buy ya decididos en el intent de viabilidad; F1 es construcción interna. |
| 8 | Veredicto de viabilidad: **GO** (riesgo bajo). | feasibility (Q1=A) | Formato JWT estándar y Bearer por header confirmados por código; D-01 acotado a transporte. |
| 9 | Alcance partido en F1-U1 (backend) → F1-U2 (cliente de red) → F1-U3 (auth nativa), todas Must. | scope-definition (Q1=A) | Camino lineal; F1-U1 desbloquea el transporte nativo. |
| 10 | Team Formation **saltada**. | team-formation (SKIP) | Único propietario-ejecutor; sin equipo ni mob. |
| 11 | UI de F1 limitada a Login + Splash; flujos de auth (login, auto-login, refresh, logout). | rough-mockups (Q1=A) | El resto de F1 no tiene UI; pantallas de datos en F2. |
| 12 | **Polish nativo del login (SwiftUI puro) DENTRO de F1**; **Face ID/Touch ID diferido** fuera de F1. | rough-mockups (petición del propietario, opción A) | Aprovecha la natividad sin inflar riesgo; Face ID amplía B-03 y se decide después. Coste 0 €, sin dependencias de terceros. |

## Sources

- Todos los artefactos de ideación de F1 y el decision-log del engine.

## Assumptions & Open Questions

None.
