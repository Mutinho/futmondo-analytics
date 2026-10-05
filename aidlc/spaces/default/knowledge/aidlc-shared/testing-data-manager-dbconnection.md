# Tests sobre `DataManagerV2` / `DBConnection`: no abrir PostgreSQL real en construcción

> Conocimiento de equipo (`aidlc-shared`): lo leen todos los agentes en cada
> intent del espacio. Patrón reutilizable aprendido en el intent
> `261005-data-manager-god-file` (descomposición del god-file
> `data_manager_v2.py`). Guía reutilizable; NO sustituye a las reglas de
> `memory/` (que solo se escriben por el ritual de learnings).

## Síntoma

Al añadir characterization tests que construyen la fachada:

```python
dm = DataManagerV2(skip_init=True)
dm.db = fake_db   # demasiado tarde
```

el gate de CI (sin PostgreSQL, por diseño — la suite usa el fake in-memory,
NFR6) falla con, potencialmente, decenas de tests a la vez:

```
psycopg2.OperationalError: connection to server on socket
"/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory
```

Puede pasar en CI (Python 3.12 + `requirements.txt` completo con
`libsql-experimental` + ruta Postgres) aunque **pase en local** (p. ej. 3.14 sin
`DATABASE_URL` o sin libsql), porque la ruta de conexión diverge entre entornos.

## Causa raíz

`DBConnection.__init__` es **eager**: construye un pool `psycopg2` y ejecuta un
`SELECT 1;` de liveness en construcción. Como `DataManagerV2.__init__` hace
`self.db = DBConnection()` (y además llama a `_ensure_schema_updates()`), la
conexión real se intenta **antes** de que el test pueda reasignar
`dm.db = fake_db`.

## Patrón correcto (test-only, sin tocar producción)

- **Fixture autouse en `conftest.py`** que respalde la conexión de
  `DBConnection` con el `_FakeInMemoryDB` del propio conftest: parchear
  `DBConnection.__init__` para que no abra pool/red y exponga
  `get_connection`/`get_cursor`/`adapt_params`/`adapt_sql` del fake. Así el hook
  de esquema que `__init__` ejecuta en construcción corre inofensivo contra
  memoria, y cada test sigue inyectando su `fake_db`.
- Alternativa equivalente ya usada en la suite (verde en CI):
  `DBConnection.__new__(DBConnection)` para construir una instancia **hueca sin
  `__init__`** (ver `test_error_layer_hardening.py`,
  `test_db_engine_characterization.py`).
- **NO** stubbear el método caracterizado `_ensure_schema_updates`: hay un test
  que lo invoca explícitamente contra su fake y debe seguir ejerciendo la
  delegación real. Neutralizar solo la *conexión*, no el comportamiento.

## Antipatrón (NO hacer)

- **NUNCA** arreglarlo levantando un servicio PostgreSQL en el workflow de CI.
  Contradice la posture afirmada (suite sin red/BD real, NFR6) y el mandato de
  coste 0 €; además trata el síntoma, no la causa (una conexión real abierta en
  construcción). El bug se corrige en los tests/fixtures, no en el pipeline.

## Aplicabilidad

Cualquier servicio cuyo `__init__` instancie `DBConnection` (o abra un recurso
real en construcción) y que se quiera ejercitar con el fake in-memory. Diseñar
los tests para inyectar el doble **sin** pasar por la apertura real.
