# NFR — Tech Stack Decisions (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

## TSD-1 — Sin dependencias nuevas
El ajuste usa solo lo ya presente: FastAPI (`Cookie`, `Header`, body Pydantic), PyJWT, el
`token_store` existente. **Cero dependencias nuevas** (coste 0 €).

## TSD-2 — Modelos Pydantic de body opcional
Se añaden `RefreshBodyOptional` y `LogoutBodyOptional` (`refresh_token: Optional[str] = None`) en
`auth/models.py`; no se reutiliza `RefreshRequest` (su campo es obligatorio y provocaría 422 en el
canal cookie).

## TSD-3 — Gate de CI sin cambios de tooling
`ruff`/`pytest`/`pip-audit`/`gitleaks` ya operativos; el bolt añade tests pytest y pasa el gate
existente sin tocar su configuración.

## Sources
- [consumes] technology-stack.md, dependencies.md, functional-spec.md, entities.md.

## Assumptions & Open Questions
None.
