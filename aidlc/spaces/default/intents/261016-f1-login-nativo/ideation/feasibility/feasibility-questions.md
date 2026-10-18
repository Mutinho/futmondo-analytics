# Feasibility & Constraints — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés. Las incógnitas técnicas de F1 se
> cerraron por lectura de código (formato JWT estándar; Bearer ya validado por header; D-01
> acotado a transporte del refresh token), así que no quedan suposiciones abiertas que
> confirmar. Sólo resta validar el veredicto.

## Q1 — Veredicto de viabilidad de F1

El assessment concluye **GO**: F1 es viable y de riesgo bajo; el ajuste de backend (D-01) es
aditivo y acotado a transporte del refresh token; el formato del JWT ya es nativo-compatible.

- A. **GO** — proceder a scope-definition con este encuadre (recomendado).
- B. GO condicionado — proceder, pero marcar alguna condición extra (especifícala).
- C. NO-GO / revisar — hay algo que replantear antes de seguir (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar feasibility, confirma el encuadre de viabilidad de F1:

- **Veredicto**: GO (riesgo bajo).
- **Formato JWT**: estándar `HS256` reutilizable por el cliente nativo sin cambios (confirmado
  en `jwt_utils.py`).
- **Bearer**: ya validado por header en `dependencies.py` → `/api/v1/*` encaja sin cambios.
- **D-01**: ajuste aditivo del backend, acotado a transporte del refresh token (body/header),
  dejando intacto el canal cookie `HttpOnly` de la PWA.
- **Restricciones durables**: coste 0 €, refresh token en iOS Keychain, idioma inglés/castellano,
  gate de CI bloqueante para el cambio de backend.
- **Dependencias de entorno** (WSL + Swift 6.4 + `xtool` + Apple ID): satisfechas por el spike F0.

¿Está todo correcto?

[Answer]: Looks correct
