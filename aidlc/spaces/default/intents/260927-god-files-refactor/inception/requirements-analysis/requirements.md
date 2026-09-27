# Requisitos — FR13 Descomposición de los god files del backend

> Intent `260927-god-files-refactor`. Deriva del análisis `260911-analisis-mejoras` (FR13, eje AX1) y del backlog `docs/BACKLOG-plan-intents.md` (Intent 3). Scope `refactor`, brownfield, depth Minimal. Conversation language: Spanish.
>
> Fuentes: `codekb/futmondo-analytics/code-structure.md` (anatomía, seams, superficie pública), `code-quality-assessment.md` (cobertura, riesgos, reglas afirmadas), `architecture.md` (acoplamiento). Decisiones fijadas en `requirements-analysis-questions.md` (Q1–Q5, confirmadas).

## Sources

- [desc] Initial description: descripción autoritativa del intent (`project-description.json`) — FR13, cuatro god files objetivo, plan incremental multi-Bolt, characterization-first, coste 0 €.
- [scope] Workflow-selected scope: `refactor` (depth Minimal, test strategy Minimal; el suelo de scope no añade piso de nuevos tests y exige que la suite existente siga verde).
- `codekb/futmondo-analytics/code-structure.md` — organización, seams de extracción y superficie pública por god file.
- `codekb/futmondo-analytics/code-quality-assessment.md` — cobertura por fichero, señales de deuda, riesgos y reglas afirmadas de la intervención.
- `codekb/futmondo-analytics/architecture.md` — acoplamiento estrella a `DataManagerV2` y patrón de referencia `prizes/`.
- [Q1]–[Q5] `requirements-analysis-questions.md` — alcance, orden, profundidad, criterio de aceptación y red de caracterización (confirmados).
- [memory:M1] Reglas afirmadas del proyecto (characterization-first, no ampliar god files, no reformatear en masa, no relajar cobertura, coste 0 €).

## Análisis de intención

El objetivo es reducir el riesgo de cambio y la deuda de mantenibilidad concentrada en los cuatro god files del backend (`data_manager_v2.py` 3692 líneas, `data_sync_service.py` 1955, `assistant_service.py` 1158, `analytics_service.py` 828), **preservando el comportamiento observable** y sin reescrituras grandes. No se busca un rediseño funcional: cada fichero conserva su superficie pública como fachada delgada que delega en módulos por dominio, replicando el precedente ya materializado en el paquete `prizes/` (capa estrecha testeable + writer transaccional atómico). El trabajo es **incremental y gated**: cada god file (o dominio dentro de él) se descompone en su propio Bolt, empezando por el de menor riesgo para validar el patrón antes de tocar el núcleo de acoplamiento. [desc] [Q1] [Q3] [architecture]

## Requisitos funcionales

### FR1 — Descomposición incremental gated de los cuatro god files
El intent aborda los cuatro god files, cada uno (o cada dominio extraído) en su **propio Bolt con aprobación**, no de golpe. [Q1] [desc]
- FR1.1: El orden de intervención es por riesgo creciente: `analytics_service.py` → `assistant_service.py` → `data_sync_service.py` → `data_manager_v2.py`. [Q2]
- FR1.2: Cada Bolt es independientemente aprobable y dejable a medias entre oleadas (se puede detener el intent tras cualquier Bolt sin dejar el código en estado incoherente).
- Criterios de aceptación:
  - Dado el plan de entrega, cuando se secuencian los Bolts, entonces el primero ataca `analytics_service.py` y el último `data_manager_v2.py`.
  - Dado el cierre de cualquier Bolt, cuando se ejecuta la suite, entonces la suite existente queda verde y el comportamiento observable no cambia.

### FR2 — Extracción a fachada delgada + módulos por dominio
Cada god file tocado se reduce a un **orquestador/fachada delgado** que preserva su superficie pública, con la lógica movida a módulos por agregado/dominio detrás de esa fachada, replicando el patrón `prizes/` + writer transaccional atómico. [Q3] [code-structure]
- FR2.1: La superficie pública se preserva exactamente: `AnalyticsService.get_*` (10 métodos), `get_assistant_service()` / `async ask(...)`, `DataSyncService.sync_*` (10 syncs) / `sync_all()`, `DataManagerV2.*` (~60 métodos consumidos por 8 routers + sync + analytics + initializer). Ningún consumidor (routers, sync, analytics) se modifica por la extracción. [code-structure] [code-quality-assessment]
- FR2.2: El acceso a datos (SQL crudo inline: 94 `cursor.execute` en `data_manager_v2`, 42 en `assistant_service`, 2 en `analytics_service`) se aísla tras repositorios/módulos por agregado; no se introduce el anti-patrón SQL-en-router. [code-structure] [memory:M1]
- FR2.3: El estado/config module-level y las cachés per-instance (`CHAMPIONSHIP_ID`/`LEAGUE_ID`, claves LLM, `_team_cache`/`_player_cache`, `cache_duration`) se pueden inyectar al extraer, **sin cambiar el comportamiento observable**. [code-quality-assessment]
- Criterios de aceptación:
  - Dado un god file descompuesto, cuando un router/consumidor invoca un método público, entonces obtiene el mismo resultado observable que antes de la extracción.
  - Dado el código extraído, cuando se inspecciona, entonces la lógica de negocio vive en módulos por dominio y la fachada solo delega.

### FR3 — Red de caracterización previa al movimiento de código (characterization-first)
Antes de mover código, el comportamiento observable afectado queda congelado con tests de caracterización, con inversión dimensionada según el riesgo del fichero. [Q5] [memory:M1] [code-quality-assessment]
- FR3.1: Para el núcleo `data_manager_v2.py` (cobertura directa ~cero, consumido por 8 routers + sync + analytics), se caracteriza **ampliamente su superficie pública** antes de iniciar su descomposición.
- FR3.2: Para `analytics_service.py`, `assistant_service.py` y `data_sync_service.py`, se caracteriza **just-enough por seam**: solo el comportamiento de los métodos/dominios que se mueven en ese Bolt, antes de tocarlos.
- FR3.3: Los tests de caracterización usan los dobles/fakes in-memory existentes (`_FakeInMemoryDB`/`_FakeCursor` de `conftest.py`, fake `DataManagerV2` por lambdas de `test_analytics_service.py`), sin red, sin BD real, sin credenciales/tokens reales.
- Criterios de aceptación:
  - Dado un seam a extraer, cuando se revisa el Bolt, entonces existe caracterización que congela su comportamiento observable ANTES del primer movimiento de código.
  - Dado `data_manager_v2.py`, cuando arranca su descomposición, entonces su superficie pública tiene caracterización amplia (no solo el seam puntual).
  - Los tests no realizan I/O de red ni acceden a BD real ni contienen credenciales (gitleaks escanea los tests).

### FR4 — Criterio de aceptación por Bolt (comportamiento preservado + seams extraídos)
El criterio de "hecho" de cada Bolt es **cualitativo**: comportamiento preservado y seams extraídos, sin umbral numérico de líneas. [Q4]
- FR4.1: Al cerrar un Bolt, la suite de caracterización de ese Bolt y la suite existente completa están verdes.
- FR4.2: Al cerrar un Bolt, al menos **un** dominio/seam (≥1) del god file tocado ha sido extraído a un módulo estrecho tras la fachada. Si delivery-planning fija un mínimo mayor por Bolt, prevalece ese número; el piso irreducible es 1.
- FR4.3: No se fija un gate duro de tamaño (líneas) que fuerce troceo artificial; la reducción de tamaño es una consecuencia, no un umbral bloqueante.
- Criterios de aceptación:
  - Dado el cierre de un Bolt, cuando se evalúa "hecho", entonces se comprueba comportamiento preservado + ≥1 seam extraído, no un número de líneas.

## Requisitos no funcionales

- **NFR1 — Mantenibilidad**: tras cada Bolt, el god file tocado tiene menor responsabilidad concentrada (dominios separados en módulos), medible por la extracción de seams y la desaparición de SQL inline del cuerpo de la fachada. [code-quality-assessment]
- **NFR2 — Preservación de comportamiento (equivalencia observable)**: ningún cambio altera el contrato observable de la superficie pública ni de los endpoints; verificado por caracterización + suite existente verde en el gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de merge a `main`. [memory:M1]
- **NFR3 — Testabilidad**: los módulos extraídos son unitariamente testeables con los fakes in-memory existentes, sin red ni BD real. [code-quality-assessment]
- **NFR4 — Coste**: coste 0 € — solo tiers gratuitos; no se introducen dependencias de pago ni tooling nuevo con coste recurrente. Cualquier librería nueva (no se prevé ninguna) sería OSS y fijada a versión exacta. [memory:M1]

## Constraints

- Mantener el stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io); sin reescrituras grandes. [desc]
- Coste 0 €: solo soluciones sostenibles en tiers gratuitos. [desc] [memory:M1]
- NO ampliar los god files ni el patrón SQL-en-router mientras se descomponen; el código nuevo va tras una capa/función estrecha testeable. [memory:M1]
- NO reformatear en masa con `ruff format` / Prettier los ficheros brownfield; formatear solo los ficheros nuevos o de forma quirúrgica. [memory:M1]
- NO bajar ni relajar umbrales/pisos de cobertura para pasar el gate; el ratchet solo sube. [memory:M1]
- Preservar la superficie pública de los cuatro servicios (los routers y consumidores no se tocan). [code-structure]
- Gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de merge a `main`; un rojo nunca llega a producción. [memory:M1]

## Assumptions

- Los `except: pass` de `data_manager_v2.py` (~29) y de `photo_service.py` quedan como **deuda registrada FUERA de alcance** (regla afirmada): se preserva el comportamiento, no se limpian oportunistamente al extraer. [assumption] [memory:M1]
- El patrón de referencia `prizes/` + `replace_team_prizes` es replicable por dominio y es el modelo de extracción esperado. [assumption] [code-structure]
- La caracterización de efecto ya existente de sync (DEGRADED/fatal, `sync_prizes`, reemplazo atómico) sigue vigente y se apoya en ella al trocear `data_sync_service.py`. [assumption] [code-quality-assessment]

## Out of scope

- Sanear los `except: pass` / broad-except de los god files (deuda registrada, no de este intent). [memory:M1]
- Cambios funcionales, de UI/UX o de contrato de API; el trabajo es refactor de estructura con comportamiento preservado. [scope]
- La deuda transversal de pinning de dependencias y comentarios obsoletos "Railway"/"Turso" (cerrada o registrada en intents previos). [code-quality-assessment]
- Descomposición de otros ficheros del backend que no sean los cuatro god files nombrados.
- Introducir o subir el piso de cobertura backend (`cov-fail-under`): hoy es observability-only (sin piso) y este intent NO lo introduce ni lo ratchetea (eso fue alcance del intent de gate hardening); la restricción "no relajar cobertura" solo garantiza que la suite existente sigue verde. [code-quality-assessment]

## Open questions

- ¿La descomposición de `data_manager_v2.py` (el núcleo) cabe en un solo Bolt o requiere sub-Bolts por grupo de dominio (schema/DDL, jugadores, transacciones, standings, …)? — se resolverá en delivery-planning a partir de la anatomía de `code-structure.md`, respetando el criterio gated por dominio de FR1.
