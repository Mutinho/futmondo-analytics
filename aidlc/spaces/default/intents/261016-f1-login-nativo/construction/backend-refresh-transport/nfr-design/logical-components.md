# NFR Design — Logical Components (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

| Componente lógico | Rol | Ubicación objetivo |
|-------------------|-----|--------------------|
| `resolve_refresh_token(cookie, header, body)` | Función pura de precedencia (SEC-4) | `auth/routes.py` (función de módulo, estrecha y testeable) |
| `RefreshBodyOptional` / `LogoutBodyOptional` | Modelos Pydantic de body opcional | `auth/models.py` |
| Handlers `login`/`refresh`/`logout` | Orquestan resolución + cripto existente | `auth/routes.py` (modificación aditiva) |
| Tests `test_auth_refresh_transport.py` | 8 tests pytest de ambos canales | `backend/tests/` |

No se crean clases ni servicios nuevos; no se amplían god-files. La única pieza "nueva" es una
función pura de resolución y dos modelos de body opcional.

## Sources
- [consumes] functional-spec.md, components.md (C6), security-design.md.

## Assumptions & Open Questions
None.
