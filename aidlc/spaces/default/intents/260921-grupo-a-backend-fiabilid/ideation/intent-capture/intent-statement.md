# Enunciado de intención — Fiabilidad de la sync de 11 pasos

> Conversation language: Spanish. Scope: `feature`. Proyecto brownfield
> futmondo-analytics. Este intent nace del Grupo A del plan de mejoras del
> intent de análisis `260911-analisis-mejoras`, reencuadrado tras verificar el
> código real en `main` (2026-09-21).

## Intención

Hacer **observables y acotados los fallos silenciosos** de la sincronización de
11 pasos del backend, para que un paso que falla deje de reportarse como éxito y
para reducir el manejo de errores demasiado amplio que enmascara la causa. Es
una intervención **acotada y aditiva** sobre el servicio de sync existente: no
reescribe el `data_sync_service.py`, no amplía los god-files y no toca el
frontend. Coste 0 €. [scope] [Q1] [Q2]

El trabajo cubre dos requisitos del eje de fiabilidad (AX3) del plan de análisis,
más un remate menor de seguridad detectado como casi cerrado:

- **FR3.1 — Visibilizar los pasos "non-critical" degradados.** Hoy los pasos que
  degradan una excepción a "no crítico" solo emiten un `logger.warning` (p. ej.
  `data_sync_service.py:224`, "Market value enrichment failed (non-critical)")
  sin reflejar el paso como **degradado** en el estado de la tarea. El usuario y
  el operador ven la tarea como completada con éxito aunque un paso haya fallado.
  Objetivo: registrar el fallo de forma visible (log estructurado **y** estado
  del paso en la tarea) para los pasos `prizes` y `phantoms`, encapsulado en una
  **función/helper estrecha reutilizable** (p. ej. `record_degraded_step(...)`)
  que otros pasos puedan adoptar en rondas futuras sin reescribir el servicio.
  [FR3.1] [Q1]

- **FR3.2 — Acotar el `except Exception`/bare-except silencioso.** Empezar por
  los `except` demasiado amplios de **arranque y migraciones** (y los que ocultan
  fallos sin distinguir recuperable de fatal), presentes hoy en varios módulos
  (`services/db_connection.py`, `auth/token_store.py`, `services/data_sync_service.py`,
  entre otros). Objetivo: distinguir error recuperable (log + continuar/reintentar)
  de fatal (propagar), sin capturar-y-silenciar. Alcance conservador: los `except`
  de arranque/migraciones y los del camino de sync tocado por FR3.1; **no** una
  purga masiva de los ~159 `except` del backend. [FR3.2] [Q2]

- **FR6 (remate) — Techo de sanidad del `price` de puja.** La validación central
  de FR6 **ya está implementada** en `market.py::place_bid` (rechazo de
  `price <= 0` con HTTP 422 antes de proxyar a Futmondo; cita `FR6/NFR1.4-1.5`).
  Queda solo un hueco menor: hoy acepta **cualquier** entero positivo sin techo
  (riesgo de overflow/abuso). Se añade un **techo de sanidad** y su test de
  regresión, como remate trivial dentro de este intent para no perderlo. El rango
  dinámico min/max del mercado queda **fuera** (evita acoplarse al estado del
  campeonato / god-file; coste). [FR6] [Q3]

## Problema y valor

- **Problema**: un sync que falla parcialmente miente sobre su resultado. Un paso
  "non-critical" que falla queda enterrado en un warning; el estado de la tarea
  dice éxito. Esto erosiona la confianza en los datos (premios, phantoms) y
  dificulta el diagnóstico. Los `except` amplios agravan el problema al tragarse
  la causa raíz.
- **Valor**: fiabilidad observable. Tras el cambio, un fallo parcial es **visible**
  (estado del paso + log estructurado) y los errores dejan de silenciarse en los
  puntos más críticos (arranque, migraciones, sync). Es la base para futuras
  rondas de endurecimiento sin reescrituras.

## Restricciones

- Coste 0 €: solo tiers gratuitos, sin dependencias con gasto recurrente. [memory:M1]
- **NO** ampliar los god-files (`data_sync_service.py`, `data_manager_v2.py`) ni
  el patrón SQL-en-router; el código nuevo va tras una capa/función estrecha
  testeable. [project.md]
- Backend-only: no se toca el frontend. [Q3]
- Test-after con specs `pytest` **significativas** (aserciones reales sobre estado
  de la tarea, log y payload rechazado), nunca `assert True`. [team.md]
- Gate de CI bloqueante (gitleaks + `pytest` + `ng test`) verde antes de fusionar
  a `main`; squash-merge, Conventional Commits en castellano. [team.md]
- Mantener el stack actual (FastAPI + Neon + Fly.io); sin reescrituras grandes.

## Sources

- [scope] Workflow-selected scope: `feature`.
- [FR3.1] [FR3.2] [FR6] Plan de mejoras: `260911-analisis-mejoras/inception/requirements-analysis/requirements.md` (eje AX3 y AX2).
- [Q1] [Q2] [Q3] Decisiones de encuadre confirmadas por el usuario en esta etapa (recomendaciones punto a punto + Opción C).
- [memory:M1] [project.md] [team.md] Reglas afirmadas en `aidlc/spaces/default/memory/`.
- Código verificado en `main` (2026-09-21): `backend/app/api/v1/endpoints/market.py:122-186` (place_bid, validación FR6 existente); `backend/app/services/data_sync_service.py:224` (patrón non-critical); `backend/app/services/task_manager.py` y `task_service.py` (reporte de progreso de la tarea).

## Assumptions & Open Questions

- [assumption] El estado de la tarea (in-memory `TaskManager` y el `task_service` durable) admite marcar un paso como "degradado" sin cambio de esquema mayor; se confirmará en diseño funcional.
- [assumption] La validación FR6 de positividad ya en producción se mantiene y no se revierte; solo se le añade el techo.
- El valor exacto del techo de sanidad del `price` se fija en diseño (un múltiplo holgado del presupuesto máximo plausible), no aquí.
