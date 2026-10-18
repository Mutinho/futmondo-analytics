# Scope Definition — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés. El alcance de F1 ya quedó muy fijado
> en intent-capture y feasibility; aquí sólo se confirma el desglose en unidades y la frontera.

## Q1 — ¿El desglose en unidades y la frontera de alcance son correctos?

El scope-document delimita F1 (ajuste de backend D-01 + cliente de red + auth nativa con
Keychain) y el intent-backlog lo parte en tres unidades Must (F1-U1 backend aditivo → F1-U2
cliente de red → F1-U3 auth nativa).

- A. **Correcto** — proceder con este alcance y desglose (recomendado).
- B. Correcto con un ajuste (especifícalo: mover algo dentro/fuera o repartir unidades distinto).
- C. Replantear el alcance (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar scope-definition, confirma el alcance de F1:

- **Dentro**: (1) ajuste aditivo del backend para transporte del refresh token (login en body;
  refresh/logout por body/header) + tests `pytest`; (2) cliente de red Swift (base URL, JSON,
  `Bearer`, errores tipados) + llamada de humo a `/api/v1/user/me`; (3) auth nativa (login,
  access en memoria, refresh token en Keychain, refresh automático, logout).
- **Fuera**: pantallas de datos, navegación/tab bar, refirmado ~7 días, widgets, push, cambios
  de backend fuera de D-01, App Store pública, Android.
- **Unidades**: F1-U1 (backend) → F1-U2 (cliente de red) → F1-U3 (auth nativa), todas Must.
- **Definición de hecho**: `pytest` verde + gate de CI + validación manual en iPhone 13 Pro; sin
  regresión de la PWA.

¿Está todo correcto?

[Answer]: Looks correct
