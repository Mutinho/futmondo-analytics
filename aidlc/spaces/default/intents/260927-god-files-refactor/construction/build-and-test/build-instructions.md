# Instrucciones de Build — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, depth Minimal, zero-Unit. Conversation language: Spanish.
>
> Backend Python/FastAPI: no hay paso de compilación; el "build" verificable es la resolución de dependencias + la suite `pytest` (que es también el gate de CI bloqueante). Coste 0 € (tiers gratuitos; venv efímero local).

## Instalación de dependencias

Desde `backend/`:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

Nota de entorno (práctica aprendida): si el Python del sistema es más nuevo que el de CI (3.12) — p. ej. 3.14 — crear un venv efímero y `pip install -r requirements.txt`. `requirements.txt` ya **no** incluye `libsql-experimental` (retirado; los tests usan el fake SQLite de `backend/conftest.py`). No se añaden dependencias nuevas en esta oleada (BR5.1, coste 0 €).

## Configuración de entorno

- `JWT_SECRET`: el arranque del servicio web exige un secreto no-default (NFR1.1). Para build/test local basta un valor efímero no productivo:

```bash
export JWT_SECRET="ci-ephemeral-secret-not-a-real-one"
```

- `DATABASE_URL`: NO se necesita para la suite; los tests usan dobles in-memory (`_FakeInMemoryDB`/`fake_db` de `backend/conftest.py`) — sin red, sin BD real, sin credenciales (NFR3, FR3.3).

## Comandos de build/verificación

Desde `backend/`:

```bash
# "Build" = resolución de imports + suite (no hay compilación en Python).
python -c "import app.main"            # verifica que el paquete importa sin errores
python -m pytest --cov=app -q          # suite completa con cobertura (gate de CI)
```

El import de `app.main` monta la app FastAPI y, transitivamente, importa `app.services.analytics_service` (ahora shim de re-export sobre `app.services.analytics.facade`), verificando que el path histórico sigue resolviendo (FR2.1, BR2.6).

## Verificación de build

- `python -m pytest --cov=app` finaliza con exit code 0.
- La línea `Required test coverage of 27% reached. Total coverage: <valor>` confirma que el piso bloqueante (`--cov-fail-under=27` en `pytest.ini`) se cumple. NUNCA se baja el piso para pasar (el ratchet solo sube).
- `ruff check --config ruff.toml app/services/analytics/` → `All checks passed!` sobre los módulos nuevos (no se reformatea brownfield, BR5.2).

## Troubleshooting

- **`ModuleNotFoundError: app...`**: ejecutar SIEMPRE desde `backend/` (`pytest.ini` fija `pythonpath = .`).
- **Fallo de arranque por `JWT_SECRET`**: exportar el valor efímero de arriba.
- **`libsql-experimental` no compila fuera de 3.12**: ya retirado de `requirements.txt`; si un venv viejo lo tiene, recrearlo.
