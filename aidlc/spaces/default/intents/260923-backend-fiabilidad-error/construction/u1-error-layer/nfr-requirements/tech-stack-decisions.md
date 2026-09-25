# Tech Stack Decisions — U1 `u1-error-layer`

- **Lenguaje/runtime**: Python 3.12 (stack fijo, sin cambios).
- **Dependencias nuevas**: ninguna. La jerarquía de excepciones son clases stdlib
  que heredan de `Exception`. Coste 0 €.
- **Ubicación**: módulo nuevo `integration_errors` bajo `backend/app/` (capa
  estrecha y testeable, fuera de los god-files).
- **Tests**: `pytest` desde `backend/`, con las fixtures compartidas de
  `conftest.py`; sin red, sin DB real, sin credenciales.
- **Lint**: `ruff` (`backend/ruff.toml`), advisory; este intent re-habilita `E722`
  advisory en commit aislado (FR3.2.3) — decisión de U1.

## Assumptions & Open Questions

None.
