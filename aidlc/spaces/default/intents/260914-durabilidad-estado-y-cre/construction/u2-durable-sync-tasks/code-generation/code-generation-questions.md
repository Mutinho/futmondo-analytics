# Code Generation Questions — u2-durable-sync-tasks

## Plan Approval

Aprobación del plan exacto de generación de código para `u2-durable-sync-tasks`, que cubre
`code-generation-plan.md` (con su Testing Contract embebido) y `unit-test-instructions.md`.

Resumen del plan (14 pasos): añadir `TaskRepository` a la capa `stores/` (ya existente) y
`TaskService`; **caracterización primero** de `TaskManager` (congelar in-memory actual); esquema
durable `sync_task` por script SQL idempotente al arranque; persistir estado/progreso de tareas
(FR1.4 consultable tras reinicio); marcar tareas en curso como interrumpida-por-reinicio al arrancar
(FR1.5, no se reanuda); unicidad 409 contra estado persistido salvo interrumpida (FR1.6); re-cableo de
`/api/v1/sync/trigger` y `/task/{id}` para delegar en `TaskService` (BD autoridad, `TaskManager` como
caché best-effort). Tests test-after por capa (Standard, 5–8 por componente) con **fakes de
persistencia** (nunca Neon real). Sin endpoints nuevos; contrato observable preservado.

**Nota de proceso:** las etapas de diseño per-unit de u2 (functional/nfr/infrastructure) quedaron
saltadas al reiniciar la etapa; este plan incorpora el diseño de la durabilidad de tareas,
fundamentado en requirements + unit-of-work + contract-summary + código brownfield. Es una decisión
a validar en esta aprobación.

Instrucciones de test (resumen): `pytest` desde `backend/`, comando por-unidad scoped a
`tests/test_durable_task_*.py`; fixture `fake_db`; cobertura como referencia (sin piso bloqueante).

[Approval Fingerprint]: sha256:v3:cd40965d207d2dd7d509875951f7b896054f6864ce67f99c75278d818c307aae
[Planned Source]: 4cca746a795ff3e5ae44dcfc151a70f83a9a776b8cde7aa3d6c3064bf326d8b3

- "Approve Plan" — proceder a generar el código
- "Request Changes" — revisar el plan

[Answer]: Approve Plan
