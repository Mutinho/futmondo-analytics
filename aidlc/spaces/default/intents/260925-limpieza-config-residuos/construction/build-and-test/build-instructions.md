# Build Instructions — FR14 + FR15 (limpieza de configuración y residuos)

Intent brownfield: no hay build nuevo, solo verificación de que el existente
sigue funcionando tras la poda. Coste 0 €.

## Dependencias

### Backend (Python 3.12 en CI; fake in-memory en tests)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # ya SIN libsql-experimental
```

Para reproducir en local a coste 0 cuando el Python del sistema es más nuevo que
el de CI (learning afirmado 2026-09-16): crear un venv efímero excluyendo
`libsql-experimental` (no compila fuera de 3.12, no lo ejercitan los tests) y
fijar un `JWT_SECRET` de arranque efímero:

```bash
grep -v libsql-experimental requirements.txt > /tmp/reqs.txt
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -r /tmp/reqs.txt
export JWT_SECRET="<efímero, no-default>"
```

### Frontend (Angular 22)

No modificado en este intent. Build habitual:

```bash
cd angular-app && nvm use   # .nvmrc = 22.22.3
npm ci && npm run build
```

## Setup de entorno

- `DATABASE_URL`: cadena Neon PostgreSQL (única fuente ahora; retiradas las
  ramas Turso/SQLite de producción). En tests no se conecta a BD real (fakes).
- `JWT_SECRET`: no-default, exigido al arranque (NFR1.1). En tests, efímero.
- `CHAMPIONSHIP_ID`/`LEAGUE_ID`: ya sin default legacy; el flujo multi-usuario
  usa datos del usuario logado.

## Comandos de build/verificación

```bash
# Backend: importabilidad + suite
cd backend && JWT_SECRET="<efímero>" python -m pytest -q

# Frontend (solo en CI o si se tocara): ng test
cd angular-app && npm test
```

## Verificación del build

- La suite backend arranca sin `ImportError` (retirada del dead-path en lockstep).
- `grep` confirma ausencia de refs vivas a los símbolos Turso/SQLite retirados.

## Troubleshooting

- `libsql-experimental` no compila fuera de Python 3.12: por eso se retira del
  `requirements.txt` (ya no hay import vivo) y se excluye en venvs efímeros locales.
- Si `ruff check` reporta avisos: son advisory y preexistentes; no bloquean ni se
  corrigen en masa (regla afirmada de no reformatear brownfield).
