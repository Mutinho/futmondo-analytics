# Code Summary — Descomposición DDD `match_odds` (piloto, Oleada 3)

Intent `sync-god-file` · stage `code-generation` · scope `refactor` · Minimal ·
Brownfield · backend-only. Equivalencia funcional estricta (FR5): sin cambio de
comportamiento observable.

## Ficheros creados / modificados

Creados (nuevos, DDD lightweight bajo `backend/app/services/sync/match_odds/`):

- `backend/app/services/sync/__init__.py` — docstring del paquete de contextos
  de sync.
- `backend/app/services/sync/match_odds/__init__.py` — re-exporta
  `MatchOddsSyncOrchestrator`.
- `backend/app/services/sync/match_odds/domain/__init__.py`.
- `backend/app/services/sync/match_odds/domain/ports.py` —
  `MatchOddsSyncDataPort` (Protocol consumer-owned, sin SQL): sólo
  `save_match_odds` y `update_sync_metadata`, las dos operaciones de
  persistencia que el dominio consume (BR2.1).
- `backend/app/services/sync/match_odds/infrastructure/__init__.py`.
- `backend/app/services/sync/match_odds/infrastructure/match_odds_adapter.py` —
  `DataManagerMatchOddsAdapter`: único punto que toca `DataManagerV2`, envuelve
  las dos llamadas **verbatim** con la misma convención de argumentos por
  palabra clave que el código inline original (BR2.2). No añade ni reescribe
  nada en `data_manager_v2.py`.
- `backend/app/services/sync/match_odds/orchestrator.py` —
  `MatchOddsSyncOrchestrator`: ingesta (cliente Futmondo inyectado) + timing +
  manejo de error + delegación en el port; devuelve el `SyncResult` idéntico.

Modificado (edición quirúrgica, sólo la delegación fina):

- `backend/app/services/data_sync_service.py` — `sync_match_odds()` reducido de
  ~56 líneas a una delegación fina al orquestador (import perezoso, misma firma
  y mismo retorno). `sync_all()` no se toca: conserva la clave literal
  `match_odds` en la misma posición (9ª, antes de `prizes`).

Test:

- `backend/tests/test_sync_match_odds_characterization.py` — red de seguridad
  characterization-first (7 tests) que congela el `SyncResult` observable y el
  orden de la clave en `sync_all()`.

## Decisiones clave

- **Forma del método real vs. plan genérico**: el `sync_match_odds` actual NO usa
  `time.sleep()` de throttling ni `try/except Integration*Error` tipado — usa un
  `except Exception` amplio. Se ha preservado ESE cuerpo verbatim en el
  orquestador (equivalencia estricta manda sobre la descripción genérica del
  plan). No se ha inventado throttling ni escalado tipado que el método no tenía.
- **Adapter con argumentos por palabra clave**: las dos llamadas inline
  originales pasaban `save_match_odds` (posicional `championship_id, matches` +
  `round_id=`/`matchday=`) y `update_sync_metadata` (todo por palabra clave). El
  adapter reproduce exactamente esa convención; sólo reenvía los kwargs que las
  llamadas originales suministraban, dejando el resto en los defaults de
  `DataManagerV2`, de modo que la fila persistida es idéntica.
- **Inyección con default de producción** (patrón `analytics`/`assistant`): el
  orquestador acepta un `MatchOddsSyncDataPort` inyectable y usa el adapter de
  producción por defecto; el facade le pasa
  `DataManagerMatchOddsAdapter(dm=self.dm)` para reusar el mismo `DataManagerV2`
  ya construido (sin re-init de esquema).
- **Sin shim de re-export** (Step 11): el único llamador
  (`app/api/v1/endpoints/sync.py:137`) invoca `sync_service.sync_match_odds()`
  sobre el facade; el método permanece, así que ningún import histórico se
  rompe. No se añade shim.
- **No credenciales en logs/excepciones** (BR4.2): el path de error registra
  `str(e)` y lo guarda como `error_message`, igual que antes; el cliente Futmondo
  ya mantiene las credenciales fuera de sus propios errores.

## Resumen de cobertura de tests

- Caracterización (Step 4, contra código ACTUAL sin cambios): **7 passed**.
- Caracterización (Step 9, contra código EXTRAÍDO): **7 passed** — equivalencia
  estricta demostrada (FR5).
- Suite completa backend (Step 10, `pytest -q --cov=app`): **251 passed,
  3 xfailed**. Cobertura total **34.56%** ≥ piso `--cov-fail-under=27` (NFR2);
  el piso NO se relajó. Los módulos nuevos quedan al 100% de líneas cubiertas.
- `ruff check` sobre los ficheros nuevos + el test: **All checks passed** (sin
  `ruff format` masivo).

### Entorno de verificación

Python local 3.14 (CI usa 3.12). Se usó el workaround del proyecto: venv efímero
excluyendo `libsql-experimental` (no está en `requirements.txt`, no lo ejercitan
los tests) y `JWT_SECRET` efímero de arranque. `pytest.ini` y el piso no se
tocaron. Tests sin red, sin BD real, sin credenciales (fakes en memoria + cliente
Futmondo doble).

## Desviaciones

- Ninguna respecto al alcance del plan (piloto `match_odds` de extremo a extremo,
  forma lightweight). Los 9 dominios restantes quedan como pasos secuenciados
  para pasadas posteriores, según el plan.
- Matiz sobre el plan: throttling / `try/except` tipado descritos en Step 6 son
  la plantilla genérica del dominio de sync; el método piloto no los contiene, y
  no se han añadido para no alterar el comportamiento observable (equivalencia
  estricta). Documentado arriba en Decisiones clave.
