# Code Summary — Backend Security Hardening

> Scope `security-patch`, depth Minimal, test strategy Minimal, brownfield,
> zero-Unit. Cinco correcciones de seguridad: FR6, FR7, FR8, FR9, FR18.
> Metodología test-after con caracterización-primero para FR9 (Testing Contract
> `sha256:332119b61a669b4846e867daee7f74367cac9b9a879942f35f06558dc4e52001`).

## Resultado de la suite

`python -m pytest -q` desde `backend/`: **135 passed, 1 warning** (VERDE).

- Baseline previo a los cambios: 125 passed.
- Neto: +10 casos (2 FR9 auth + 3 FR6 + 3 FR7 + 1 FR18 + 1 neto por la
  actualización trazable en `test_durable_session_characterization.py`).
- La warning es preexistente (`StarletteDeprecationWarning` de `TestClient`),
  ajena a este patch.

Entorno de ejecución (coste 0 €): venv efímero con Python del sistema (3.14,
más nuevo que el 3.12 de CI), **excluyendo `libsql-experimental`** (no compila
fuera de 3.12 y los tests usan el fake SQLite), con `JWT_SECRET` de arranque
efímero no productivo.

## Cambios por FR

### FR9 — `is_refresh_token_valid` (NFR1.3)
`backend/app/auth/token_store.py`: se reemplazó el ternario de precedencia
ambigua por una normalización inequívoca de `expires_at` a *aware* UTC (si es
naive, se asume UTC) y una comparación directa. Un token aware futuro ahora
devuelve `True`; expirado (aware o naive), revocado o ausente devuelven `False`.

Test-after (caracterización actualizada de forma trazable):
- `test_auth_characterization.py`: el test que congelaba el bug se renombró y
  ahora afirma el contrato correcto (aware futuro → `True`); se añadió la
  regresión aware pasado → `False`. Se mantienen naive futuro/pasado, revocado y
  ausente.
- `test_durable_session_characterization.py`: este fichero también congelaba el
  mismo bug (item (c), explícitamente marcado como "out of scope for this unit").
  Como FR9 lo corrige, se retiró de forma trazable la aserción de fallo y se
  reemplazó por la del contrato correcto, actualizando el log de trazabilidad de
  su cabecera. El propio fichero anticipaba esta actualización.

### FR6 — Validación de `price` en `place_bid` (NFR1.4/1.5)
`backend/app/api/v1/endpoints/market.py`: al inicio del `try`, antes de resolver
el cliente Futmondo o cualquier efecto lateral, `price <= 0` lanza
`HTTPException(422, "El precio de la puja debe ser un entero positivo")`. El
`except HTTPException: raise` existente la propaga como 422 (no 500) y no se
reenvía la puja a Futmondo.

Test-after: `test_market_bid_validation.py` (nuevo) — price=0 → 422 y cliente NO
invocado; price negativo → 422; price>0 → cliente invocado (happy path). Doble
espía de `get_user_futmondo_client`; sin BD ni red.

### FR7 — Exposición del endpoint de fotos (NFR1.6)
`backend/app/main.py`: SIN cambio funcional. Se documentó en inglés que
`GET /api/v1/photos/{player_id}` está protegido por `AuthMiddleware` (no está en
`AUTH_EXCLUDED_PATHS`) y que `/static/photos/*` es superficie pública
INTENCIONADA (fuera del prefijo protegido; fotos no sensibles).

Test-after: `test_photos_exposure.py` (nuevo) — congela: la ruta no está en
`AUTH_EXCLUDED_PATHS`; petición sin Bearer → 401; `/static/photos` fuera del
prefijo protegido.

### FR8 — Eliminación de `SSL_VERIFY=0` (NFR1.8)
`docker-compose.yml`: se eliminó la entrada huérfana `environment: - SSL_VERIFY=0`
del servicio `backend` (y la clave `environment:` que quedaba vacía). Ningún
módulo Python consumía el flag; ausente de `fly.toml`.

Test-after: `test_tls_verification.py` (nuevo) — aserción estática: `SSL_VERIFY`
ausente de `docker-compose.yml`; ningún cliente HTTP de `backend/app/**` usa
`verify=False`. Verificado en el escaneo: 0 ocurrencias de `verify=False` en
producción.

### FR18 — Guarda de administración de BD (NFR1.9)
**Sin cambio de código.** `backend/app/api/v1/endpoints/reset_db.py::_require_db_admin`
ya devuelve 404 por defecto y acepta `{1, true, yes, on}`. `reset_db.py` NO se
tocó.

Consolidación en test: `test_db_admin_guard.py` — se añadió un caso afirmativo
alternativo (`ENABLE_DB_ADMIN=true`) que congela el conjunto aceptado, además de
los existentes (404 por defecto, 404 no-afirmativo `0`, 200 con `1`).

## Decisiones clave

- **Doble corrección trazable del mismo bug FR9**: dos ficheros de
  caracterización congelaban el bug de `is_refresh_token_valid` (auth y
  durable-session). Ambos se actualizaron al contrato corregido de forma
  trazable, como exige la metodología (los tests que describen un fallo se
  actualizan cuando el comportamiento cambia a propósito). El fichero
  durable-session ya documentaba en su cabecera este patrón de retirada.
- **Estilo de código**: los 3 ficheros de test NUEVOS se formatearon con
  `ruff format` (quirúrgico) y pasan `ruff check` limpio. NO se corrió
  `ruff format` sobre ningún fichero brownfield modificado; se verificó por
  comparación con HEAD que mis ediciones no introducen NINGÚN hallazgo `ruff`
  nuevo (los hallazgos preexistentes E402/F401/F841/I001 son deuda brownfield,
  advisory en CI).
- **Idioma**: identificadores/docstrings/comentarios en inglés; `HTTPException.detail`
  y prosa en castellano, conforme a la decisión Q4 del equipo.
- **FR18 sin cambio de código**: la guarda ya era correcta; se prefirió
  consolidar cobertura antes que tocar código funcionando (riesgo innecesario en
  un scope de patch).

## Invariantes de seguridad (no regresión) — verificadas

- No se reintrodujo password Futmondo en claro ni `JWT_SECRET` por defecto.
- No se abrieron rutas protegidas ni se añadieron exclusiones al middleware
  (FR7 es solo documentación + test que congela).
- No se amplió el SQL-en-router ni los god-files de `services/`.
- Coste 0 €: sin dependencias de pago nuevas.
- Ningún target de calidad medible se relajó para pasar un paso.

## Hueco/nota conocida (fuera de esta etapa)

Documentado ya en `team.md`: el job `verify` de `fly-deploy.yml` (push→`main`)
corre `pytest -q` sin `--cov` ni gitleaks, no idéntico al gate de MR. No lo
aborda este patch (diseño de pipeline); relevante a FR5 pero fuera de FR6-FR9/FR18.

## Ficheros creados / modificados

Modificados:
- `backend/app/auth/token_store.py` (FR9)
- `backend/app/api/v1/endpoints/market.py` (FR6)
- `backend/app/main.py` (FR7, docs)
- `docker-compose.yml` (FR8)
- `backend/tests/test_auth_characterization.py` (FR9)
- `backend/tests/test_db_admin_guard.py` (FR18)
- `backend/tests/test_durable_session_characterization.py` (FR9, actualización trazable)

Creados:
- `backend/tests/test_market_bid_validation.py` (FR6)
- `backend/tests/test_photos_exposure.py` (FR7)
- `backend/tests/test_tls_verification.py` (FR8)
