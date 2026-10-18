# Unit Test Instructions — `backend-refresh-transport` (Bolt 1 de F1)

> Fase: construcción (code-generation). Cómo ejecutar y verificar los tests del bolt. Idioma:
> castellano; tokens técnicos verbatim en inglés.

## Alcance de tests

Fichero nuevo: `backend/tests/test_auth_refresh_transport.py` — 8 tests que aseveran el efecto del
transporte del refresh token (ambos canales), con fakes in-memory (patrón `conftest.py`), sin red,
sin BD real y sin tokens reales (los tokens se generan en el test con la cripto real sobre un
`JWT_SECRET` efímero del fixture).

Casos (del functional-spec):
1. `login` devuelve `refresh_token` en el body **y** fija la cookie.
2. `refresh` por cookie **sin body** → 200 y **no 422**.
3. `refresh` por header `X-Refresh-Token` → 200.
4. `refresh` por body `{refresh_token}` → 200.
5. `refresh` sin token por ningún canal → 401.
6. `logout` por header y por body revoca → `refresh` posterior con ese token → 401.
7. Precedencia observable: cookie=T_cookie(U_cookie) + body=T_body(U_body) → el access token
   devuelto tiene `sub == U_cookie`.
8. Borde cookie-revocada + body-válido → 401 (gana la cookie; el body no se acepta).

## Cómo ejecutar (coste 0 €, según learning del proyecto)

Cuando el Python del sistema sea más nuevo que el de CI, crear un venv efímero excluyendo
`libsql-experimental` (no compila fuera de 3.12 y no lo ejercitan los tests, que usan el fake
SQLite) y fijar un `JWT_SECRET` de arranque efímero:

```bash
# desde backend/
python -m venv .venv-ephemeral
. .venv-ephemeral/bin/activate
grep -v '^libsql-experimental' requirements.txt > /tmp/reqs-notdurso.txt
pip install -r /tmp/reqs-notdurso.txt
JWT_SECRET=ephemeral-not-a-real-one python -m pytest tests/test_auth_refresh_transport.py -q
```

Además, la suite completa debe seguir verde (characterization-first):
```bash
JWT_SECRET=ephemeral-not-a-real-one python -m pytest -q
```

El gate de CI (`ruff check` + `pytest` + `pip-audit` + gitleaks) corre igual en el PR; no se
cambia su configuración.

## Testing Contract

Methodology: test-after (team.md). Tests que aseveran el efecto (payload/estado), nunca
`assert True` ni specs espejo. Scope `feature`: regresión existente verde + nuevos tests por
requisito. El piso de cobertura backend heredado (`--cov-fail-under`) solo sube, nunca baja.

## Sources

- [consumes] functional-spec.md, requirements.md (NFR-3), team-practices.md; learning de venv
  efímero del proyecto.

## Assumptions & Open Questions

None.
