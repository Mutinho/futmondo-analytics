# Unit Test Instructions — Descomposición DDD de `data_sync_service.py`

Estrategia de test: **Minimal** (scope `refactor`) · Brownfield · backend Python 3.12.

## Framework y configuración

- **Framework**: `pytest` + `pytest-cov` (ya presentes; sin dependencias nuevas).
- **Ubicación**: tests backend bajo `backend/tests/` (sin árbol de tests nuevo).
- **Fixtures**: los fakes en memoria de `backend/conftest.py`
  (`_FakeInMemoryDB`/`_FakeCursor` sobre SQLite `:memory:`, `clean_jwt_env`,
  `fake_db`). **Sin red, sin BD real, sin credenciales/tokens reales** (gitleaks
  escanea también los tests).
- El cliente externo (`FutmondoClient`/Sofascore) se sustituye por un doble/fake
  inyectado vía `DataSyncService.__init__` (ya inyectable), no por red.

## Comando exacto (acotado a este dominio)

Ejecutar SOLO los tests de caracterización del dominio en curso, desde `backend/`:

```bash
cd backend && python -m pytest tests/test_sync_match_odds_characterization.py -q
```

(Para cada dominio siguiente, sustituir por su fichero:
`tests/test_sync_<domain>_characterization.py`.) **No** usar un `pytest` de
proyecto entero para el ciclo por dominio; la suite completa se corre solo en el
Step 10 de verificación y en Build and Test.

## Alcance de tests (Minimal, dirigido por requisito)

- **Uno por comportamiento observable a preservar**, al nivel más estrecho que lo
  reproduce:
  - El `SyncResult` de `sync_<domain>()`: `status` observable
    (`success`/`no_new_data`/`error`/variante `no_*` del dominio),
    `records_synced`, presencia de `duration_seconds`.
  - La clave literal del dominio en el dict de `sync_all()` (p. ej. `match_odds`;
    para rankings, `team_standings`).
  - El modo de fallo tipado donde aplique: recuperable → efecto observable
    (degrada/continúa); fatal en punto de escritura → excepción propagada y sin
    datos a medias.
- **Piso happy-path por componente** nuevo (orquestador/adapter): al menos un test
  de camino feliz.
- Specs que **aseveran el efecto** (payload/estado/modo de fallo). **NUNCA**
  `assert True` ni specs espejo que capturan sin aseverar.

## Cobertura

- Piso backend `--cov-fail-under=27` (line-only) en `pytest.ini`: **no se relaja**;
  solo sube por trinquete. La caracterización nueva puede subir la cobertura.
- La suite existente se mantiene **verde** (scope floor `refactor`).

## Mocking / stubbing

- Doble del cliente externo (Futmondo/Sofascore) que devuelve payloads fijos de
  prueba, inyectado en el constructor.
- `fake_db`/`_FakeInMemoryDB` para la persistencia; verificar el estado escrito vía
  el fake, no contra una BD real.
- Para el patrón set-replacement (prizes/`replace_team_prizes`), aseverar el
  reemplazo atómico observable (conjunto final correcto, sin filas stale) con el
  fake.

## Gestión de datos de test

- Datos de prueba mínimos y deterministas construidos en el propio test o en
  factorías locales; nada de fixtures compartidas mutables entre tests.
- Sin credenciales/tokens reales en ningún fichero de test.
