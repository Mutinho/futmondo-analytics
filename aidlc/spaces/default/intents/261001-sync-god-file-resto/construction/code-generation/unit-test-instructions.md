# Unit Test Instructions — dominio `clauses` (`261001-sync-god-file-resto`)

> Scope `refactor`, test strategy Minimal, brownfield. Tests con dobles/fakes en
> memoria (patrón `conftest.py`), sin red, sin BD real, sin credenciales/tokens
> reales (gitleaks escanea los tests). Idioma de tests: identificadores/
> docstrings en inglés.

## Framework y configuración

- Framework: `pytest` + `pytest-cov` (ya presentes en `backend/`).
- Fixtures en memoria de `backend/conftest.py`: `_FakeInMemoryDB` / `_FakeCursor`
  (SQLite `:memory:`), `clean_jwt_env`, `fake_db`. Para caracterizar las llamadas
  a `DataManagerV2` se usa un doble/fake de `DataManagerV2` que registra
  método + argumentos invocados.
- Sin dependencias nuevas (stdlib suficiente).

## Cómo correr los tests de ESTA unidad (comando exacto, scoped)

Desde `backend/`:

```bash
pytest backend/tests/test_sync_clauses_characterization.py -q
```

Este comando está scoped al fichero de caracterización de `clauses` únicamente;
NO uses `pytest` a secas (eso reejecutaría toda la suite). El comando debe ser
runnable ANTES del primer ciclo (characterization-first): el runner ya existe en
el proyecto, así que se verifica, no se bootstrapea.

Verificación de equivalencia completa (suite entera + piso de cobertura), que
corre Build and Test, no esta unidad:

```bash
pytest -q --cov=app --cov-fail-under=27
```

## Alcance de tests (Minimal strategy)

- Un test por requisito al nivel más estrecho:
  - `SyncResult` observable de `sync_clauses` congelado (claves + tipos exactos) — FR7.1.
  - Llamadas a `DataManagerV2` congeladas (métodos + argumentos) — FR7.2.
  - Camino recoverable: paso marcado `DEGRADED`, operación no falla — FR6.2 (sólo si el comportamiento ya existe hoy para `clauses`).
  - Camino fatal: excepción tipada propagada; sin datos a medias — FR6.2 (idem).
  - No-credenciales-en-logs en el manejo de error — FR6.3.
- Floor happy-path por componente nuevo (orchestrator, adapter).
- La suite existente permanece verde (scope floor refactor).

## Cobertura

- Piso `--cov-fail-under=27` (line-only) NO se relaja; el ratchet sólo sube
  (NFR2.1). Si aparece flapping, se arregla el test no-determinista, nunca se
  baja el piso.

## Mocking / stubbing

- `FutmondoClient`: fake inyectado que devuelve payloads deterministas o lanza
  `IntegrationTimeoutError` / `IntegrationBanError` según el caso de test.
- `DataManagerV2`: fake que registra las llamadas (método + args) para aseverar
  la delegación verbatim del adapter.
- Nada de red ni BD real.

## Gestión de datos de test

- Payloads de ingesta mínimos y deterministas inline en el test o en helpers del
  propio fichero; sin fixtures compartidas mutables; nombres de variables que
  expresen su propósito (`degraded_round`, `banned_response`).
