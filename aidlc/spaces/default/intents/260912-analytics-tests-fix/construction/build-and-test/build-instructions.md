# Instrucciones de Build — Backend (Futmondo Analytics)

## Prerrequisitos
- Python 3.12 (el CI usa 3.12; wheels de `libsql-experimental` no compilan en 3.14).
- `pip` para instalar `backend/requirements.txt`.

## Instalación de dependencias
Desde `backend/`:
```bash
python -m pip install -r requirements.txt
```

## Entorno
- Variable requerida por el fail-fast de seguridad: `JWT_SECRET` (no vacío).
  En CI: `JWT_SECRET: ci-ephemeral-secret-not-a-real-one`.
- Config en `backend/pytest.ini` (`pythonpath = .`).

## Comando de build/verificación
Este intent es un bugfix de tests; no hay build compilado del backend. La
verificación es la ejecución de la suite (ver test-results.md):
```bash
JWT_SECRET=ci-ephemeral-secret-not-a-real-one python -m pytest tests -q
```

## Troubleshooting
- `ModuleNotFoundError: No module named 'dotenv'` / imports de la app: faltan
  dependencias; instalar `requirements.txt`.
- `RuntimeError: FATAL: JWT_SECRET must be set`: exportar `JWT_SECRET`.
- `libsql-experimental` no compila en Python 3.14: usar Python 3.12 (como el CI),
  o omitir esa dependencia si solo se ejecutan los tests de analítica (no la usa).
