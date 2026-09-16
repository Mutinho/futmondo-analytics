# Unit Test Instructions — u2-durable-sync-tasks

> Etapa Code Generation (Construction). Instrucciones de test para ESTA unidad. Estrategia
> **Standard** (5–8 tests por componente). Metodología test-after con caracterización primero.
> Backend `pytest` desde `backend/`. Coste 0€: fakes de la capa de persistencia, nunca Neon real.

## Framework y configuración

- **Framework**: `pytest` + `pytest-cov` (ya en el backend).
- **Config existente**: `backend/pytest.ini` (`testpaths = tests`, `pythonpath = .`); ejecutar
  siempre desde el directorio `backend/`.
- **Aislamiento**: reutilizar `backend/conftest.py` — la fixture `fake_db` (almacén en memoria que
  respeta el contrato de `db_connection`) ya añadida en u1 sirve para `TaskRepository`. Cada test
  crea y limpia su propio almacén; nunca se comparte estado mutable entre tests.

## Cómo ejecutar los tests DE ESTA UNIDAD (comando exacto, scoped)

Los archivos de test de esta unidad viven bajo `backend/tests/` con prefijo `test_durable_task_`.
Comando exacto por-unidad (NO usar un `pytest` global):

```bash
# desde backend/
pytest tests/test_durable_task_characterization.py \
       tests/test_durable_task_repository.py \
       tests/test_durable_task_service.py \
       tests/test_durable_task_api.py -q
```

Con cobertura (referencia global, sin piso bloqueante adicional):

```bash
# desde backend/
pytest tests/test_durable_task_characterization.py \
       tests/test_durable_task_repository.py \
       tests/test_durable_task_service.py \
       tests/test_durable_task_api.py \
       --cov=app.services.task_service \
       --cov=app.stores -q
```

> El runner debe estar listo (Step 2 del plan) antes del primer test. Para test-after, se implementa
> cada capa y luego se escriben/ejecutan sus tests con estos comandos.

## Alcance de tests por componente (Standard: 5–8 por componente)

- **Caracterización** (`test_durable_task_characterization.py`): congelan el comportamiento ACTUAL de
  `TaskManager` (deben pasar contra el código de hoy): tarea in-memory se pierde tras reinicio;
  `get_active_task` marca stale a los 10min; cap de 20 tareas.
- **TaskRepository / stores** (`test_durable_task_repository.py`): persistencia y lectura por
  `task_id`; consulta de tarea activa por `championship_id` contra BD; marcado masivo
  interrumpida-por-reinicio al arrancar; idempotencia; SQL parametrizado.
- **TaskService** (`test_durable_task_service.py`): tarea consultable tras "reinicio" (caché vacío →
  BD, FR1.4); unicidad 409 contra BD (FR1.6); relanzable si interrumpida; marcado al arranque
  (FR1.5); no reanuda automáticamente; BD autoridad, caché best-effort.
- **API / endpoints** (`test_durable_task_api.py`): `/task/{id}` devuelve estado tras reinicio (FR1.4);
  `/trigger` da 409 contra estado persistido y permite relanzar si interrumpida (FR1.6).

## Objetivos de cobertura

- Referencia global del scope `feature`: 80% líneas (NO piso bloqueante adicional, decisión Q3).
- **Exigido**: tests que cubran los **caminos nuevos y de error** de la durabilidad de tareas; sin
  piso porcentual bloqueante adicional. No existe `cov-fail-under` en el repo (ratcheting diferido).

## Mocking / stubbing

- **Fakes de persistencia** (fixture `fake_db`) en lugar de Neon. No mockear a nivel de driver SQL.
- **Sync worker / DataSyncService**: en los tests de servicio/API se mockean las llamadas de sync
  reales; el foco es la persistencia y las transiciones de estado, no la sincronización de datos.

## Gestión de datos de test

Cada test construye su propio almacén en memoria (`fake_db`) y lo descarta al terminar; sin fixtures
de datos compartidos mutables. La caracterización usa el código actual sin tablas nuevas; los tests
del nuevo contrato usan el fake de persistencia con la tabla `sync_task` simulada.
