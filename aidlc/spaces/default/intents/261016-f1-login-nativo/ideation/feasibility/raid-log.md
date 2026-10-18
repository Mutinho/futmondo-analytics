# RAID Log — F1: Login nativo end-to-end

> Fase: ideación (feasibility). Risks, Assumptions, Issues, Dependencies. Idioma: castellano;
> tokens técnicos verbatim en inglés.

## Risks

| ID | Riesgo | Prob. | Impacto | Mitigación |
|----|--------|-------|---------|------------|
| R-01 | El ajuste aditivo de D-01 introduce una regresión en el canal cookie de la PWA. | Baja | Alto | Ajuste estrictamente aditivo; tests `pytest` que cubren login/refresh/logout por cookie **y** por body/header; el gate de CI bloquea antes de `main`. |
| R-02 | Mal manejo del Keychain (token legible, no borrado en logout) debilita la seguridad. | Media | Alto | Criterio de hecho explícito: refresh token sólo en Keychain, borrado en logout; revisión de seguridad en diseño. |
| R-03 | Divergencia de comportamiento entre cliente nativo y PWA en el refresh (reintentos, expiración). | Media | Medio | Espejar el flujo de `auth.service.ts` (Q3=A: un reintento ante 401, re-login si refresh inválido). |
| R-04 | Fricción de firma gratuita (~7 días) estorba la validación manual en el iPhone. | Media | Bajo | Validación manual puntual; el refirmado recurrente es B-09 (fuera de F1). |

## Assumptions

| ID | Supuesto | Estado |
|----|----------|--------|
| A-01 | El formato del JWT es estándar y reutilizable por un cliente nativo sin cambios. | **Confirmado** por lectura de `jwt_utils.py` (ya no es supuesto). |
| A-02 | El header `Authorization: Bearer` ya se valida en el backend para `/api/v1/*`. | **Confirmado** por lectura de `dependencies.py`. |
| A-03 | El cómo exacto del transporte del refresh token (header vs. body) se decide en diseño. | Abierto; no afecta a la viabilidad. |

## Issues

| ID | Incidencia | Estado |
|----|-----------|--------|
| I-01 | — | Ninguna abierta en ideación. |

## Dependencies

| ID | Dependencia | Estado |
|----|-------------|--------|
| D-01 | Ajuste aditivo del backend para transporte del refresh token por body/header. | **En alcance de F1** (Q4=A). Acotado a transporte. |
| D-02 | Cadena de build nativa (WSL + Swift 6.4 + usbmuxd + `xtool`). | Satisfecha por el spike F0 (`261016-xtool-spike`). |
| D-03 | Apple ID gratuito para firma/instalación. | Satisfecha (validada en el spike F0). |

## Sources

- [consumes] intent-statement de F1.
- [code] `jwt_utils.py`, `dependencies.py`, `auth/routes.py`, `auth.service.ts`.
- [spike] `261016-xtool-spike` (D-02, D-03 satisfechas).

## Assumptions & Open Questions

None.
