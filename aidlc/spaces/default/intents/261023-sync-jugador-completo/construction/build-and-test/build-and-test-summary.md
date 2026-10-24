# Build and Test Summary — Enriquecimiento del sync de jugadores

## Estado general

- **Build:** Success (importable; `ruff check` limpio sobre los ficheros tocados).
- **Tests:** 463 passed, 3 xfailed (legacy), 0 failed. Cobertura 60,82% (piso 27% intacto).
- **Prerequisitos:** `JWT_SECRET` efímero; venv sin `libsql-experimental` si Python > 3.12.

## Inventario de tipos de test

| Tipo | Fichero | Estado |
|---|---|---|
| Unit (migración/upsert/orquestador/lectura) | 4 ficheros nuevos (23 tests) | Ejecutado, verde |
| Integration (frontera sync→players→favorites_read) | `integration-test-instructions.md` (apunta a los tests de componente verdes) | Ejecutado, verde |
| Security | `security-test-instructions.md` (SQL param + no-credenciales) | Ejecutado, verde |
| Performance | `performance-test-instructions.md` | N/A (no cambia latencia) |

(Estrategia **minimal**: no se crean suites de carga nuevas.)

## Cobertura por componente

- `favorites_read.py` 100%; el resto de las capas tocadas cubierto por sus tests.

## Target Verification Matrix

| Target ID | Expected | Actual | Verdict |
|---|---|---|---|
| T-TESTS | suite verde | 463 passed, 0 failed | **Met** |
| T-COV | ≥ 27% | 60,82% | **Met** |
| T-LINT | ruff limpio | All checks passed | **Met** |
| T-CONTRACT | 20 claves byte-identical | congelado | **Met** |
| T-MIGRATION | ALTER idempotente | verificado | **Met** |
| T-EXTRACT | 6 campos + NaN norm | verificado | **Met** |
| T-SEC-CREDS | sin credenciales | verde | **Met** |

## Readiness

- **Build-ready:** sí. **Test-ready:** sí (suite verde, piso intacto).
- **Deployment-ready:** sí; los campos nuevos se poblarán en el primer sync tras
  el deploy (sin backfill forzado, por diseño).

## Limitaciones / pendientes

- 3 `xfailed` legacy preexistentes (no de este intent).
- Deuda preexistente (fuera de alcance, señalada por el reviewer): `save_players_batch`
  referencia columnas `value`/`role2` no declaradas en el esquema versionado — no
  introducida por este intent.
