# Evidencia — Practices Discovery (re-run brownfield)

> Registro de lo inspeccionado e inferido para este borrador. Re-run brownfield:
> la base son las prácticas ya afirmadas; sólo se ajusta al matiz de fiabilidad
> backend (FR3.2 + FR4).

## Fuentes inspeccionadas

### Línea base afirmada (memoria del espacio)

- `aidlc/spaces/default/memory/team.md` — cinco secciones afirmadas (Way of Working,
  Walking Skeleton, Testing Posture, Deployment, Code Style). Base de la que se
  arrastran: trunk-based + squash a `main`, gate de CI bloqueante (gitleaks + `pytest`
  + `ng test`), test-after con specs significativas, characterization-first al endurecer
  brownfield, prohibición de `ruff format` masivo, coste 0 €.
- `aidlc/spaces/default/memory/project.md` — § Mandated (coste 0 €, gate bloqueante,
  characterization-first de `sync_prizes`/`SessionStore`/`TaskManager`, `JWT_SECRET`
  no-default), § Forbidden (no ampliar god-files ni SQL-en-router, no `ruff format` masivo,
  no contraseña en claro), § Corrections (verificar `npm ci`/`ng test` en `node:22.22.3`;
  venv efímero excluyendo `libsql-experimental` para pytest local a coste 0).
- `aidlc/spaces/default/memory/org.md` — defaults del framework (trunk-based, squash,
  base/target `main`; test-after por defecto; deploy on-merge con gate humano en prod).

### Evidencia de ingeniería inversa (RE, codekb)

- `codekb/futmondo-analytics/code-quality-assessment.md` — **propietario del detalle de
  deuda de fiabilidad**. Confirma:
  - Base sólida recuperable-vs-fatal parcial: `sofascore_client.py` (patrón de referencia
    `SofascoreIPBanError` con `except <Typed>: raise` antes del genérico), `db_connection.py`
    (rollback + raise; pool con retry x3; 9 ramas amplias), `sync_step_status.record_degraded_step`
    (FR3.1, ya caracterizado), `task_service._cache_call` (autoridad DB vs best-effort),
    arranque resiliente en `main.py`.
  - **Hueco central FR4**: `futmondo_client._make_request` colapsa `Timeout`/`RequestException`/
    `JSONDecodeError` a `None`; `login()` → `bool`, getters → `Optional`. Cambio de contrato
    de **blast radius alto** (muchos `sync_*`/`get_*` del god-file asumen `None == sin datos`).
  - **FR3.2**: 29 ramas `except Exception` en `data_sync_service.py` (0 bare-except; localizadas
    por línea); 3 `except: pass` reales en `data_manager_v2.py` (L57-58, L68-69, L672-673, SKIMMED)
    + otro en `photo_service.py` (L475-476); total `except: pass` en `app/services/`: 4.
  - **Punto de corromper-datos**: `DELETE FROM team_prizes ... matchday NOT IN (...)` (L1846)
    tras `commit()` previo (L1825), con `try/except → logger.warning` (L1859) que **traga el
    fallo de limpieza** dejando la caché en estado mixto sin señal al consumidor.
- `codekb/futmondo-analytics/technology-stack.md` — dos clientes HTTP con contratos de fallo
  divergentes: `requests` (Futmondo, sus `Timeout`/`RequestException` son las que se tragan a
  `None`) y `curl_cffi` (Sofascore, base de `SofascoreIPBanError`). Fixtures de test en memoria
  (`conftest.py`) sin red/DB/credenciales, coste 0 €.
- `codekb/futmondo-analytics/code-structure.md`, `architecture.md`, `dependencies.md` —
  estructura de servicios, god-files a no ampliar, mapa de dependencias.

### Artefactos de ideación del intent

- `ideation/scope-definition/scope-document.md` — alcance (FR3.2 primera oleada: `main.py`,
  `scripts/migrate_*`, `db_connection.py`; FR4: excepción tipada en `futmondo_client.py`,
  estado degradado vía `sync_step_status.py`, documentación de contratos), fuera de alcance
  (29 capturas de `data_sync_service.py`, resto de broad-except, poda de config muerta,
  descomposición de god-files → intents futuros), secuenciación dependencia-primero.
- `ideation/feasibility/constraint-register.md` — restricciones duras: stack fijo (C-T1),
  sin reescrituras grandes (C-T2), no ampliar god-files (C-T3), reusar `sync_step_status.py`
  (C-T4), excepción tipada propagada sin `return None` silencioso (C-T5), sin dependencias de
  pago (C-T6), gate CI bloqueante (C-O2), test-after + characterization-first (C-O3), no
  reformatear en masa (C-O4), coste 0 € (C-E1).

## Hallazgo de evidencia relevante a FR3.2 (destacado)

- **`E722` (bare-except) está en el `ignore` de `backend/ruff.toml`**
  (`select = ["E","F","I"]`, `ignore = ["E501","E402","E722"]`), y `ruff check` es
  **advisory** (`continue-on-error`) en CI. Consecuencia: hoy el linter **NO** vigila los
  `except:` desnudos. Cualquier objetivo de FR3.2 que quiera enforcement de bare-except
  deberá **re-habilitar `E722` por trinquete**, aislando el reflow de la regla afirmada de
  NO reformatear brownfield en masa. Es evidencia directa de por qué la deuda de bare-except
  pasó desapercibida.

## Inferencias

- La posture de testing del intent es **characterization-first antes de endurecer** cualquier
  broad-except tocado y el contrato de `futmondo_client` antes de cambiarlo, dentro del marco
  afirmado test-after; se infiere de C-O3 + el mandato afirmado + el blast radius alto del
  cambio de contrato FR4.
- Walking skeleton **OFF**: sistema ya en producción con pipeline maduro; nada que arrancar
  de cero (coherente con la línea base afirmada OFF).

## Contribuciones de la revisión ciega (tres agentes)

- **aidlc-quality-agent** — posición clave: **floor de aserción significativa** para specs
  de modo de fallo; un `pytest.raises` sin aseverar el efecto lateral replicaría la brecha de
  meaningfulness de FR17.1 en el backend. También: pedir decisión explícita sobre el `--cov`
  (observabilidad-only vs piso) y el inventario de llamadores de `_make_request` como entrega
  verificable; el enforcement de `E722` no es medible mientras `ruff check` sea advisory.
- **aidlc-developer-agent** — posición clave: la jerarquía de excepciones nueva debe vivir en
  un **módulo `integration_errors` dedicado con raíz común `IntegrationError`** (no colgar de
  `SofascoreIPBanError`, que acopla cross-client `requests` vs `curl_cffi`); el **alcance de la
  señalización de fallo** del cliente (¿sólo `_make_request` o también `login()`/getters?) está
  sin delimitar; el modo de fallo se traduce a acción en el llamador; mensajes de excepción
  internos en inglés.
- **aidlc-devsecops-agent** — posición clave: falta una regla dura de que la excepción tipada
  **NUNCA incluya password/token** en mensaje, `repr` ni `exc_info`; la decisión de `E722` debe
  ser un binario explícito (advisory-ahora vs diferir); el cambio de `ruff.toml` es de una línea
  de config y va en commit aislado sin `--fix`/`format`; gitleaks bloquea en ambos caminos, así
  que la asimetría `--cov` es sólo de señal.

## Decisiones de la entrevista humana (Q1-Q6, todas = A)

- **Q1 = A**: floor explícito de aserción significativa — cada spec de error asvera el EFECTO
  (recuperable → paso `DEGRADED` y la operación no falla; fatal → excepción tipada propagada y
  sin datos a medias). Nada de `pytest.raises` sin aserción de estado.
- **Q2 = A**: re-habilitar `E722` (bare-except) como **ADVISORY** por trinquete — quitarlo del
  `ignore` de `backend/ruff.toml` para que `ruff check` lo reporte, sin promover ruff a
  bloqueante; aislar el reflow (sólo la regla, sin reformateo masivo).
- **Q3 = A**: las excepciones de integración viven en un **módulo dedicado `integration_errors`**
  con raíz común `IntegrationError` y subtipos por modo de fallo, del que heredan Sofascore y
  Futmondo; capa estrecha y testeable fuera de los god-files.
- **Q4 = A**: cambio de contrato FR4 **characterization-first** — inventario verificable de
  llamadores de `_make_request` como entregable; migrar el núcleo (`_make_request` + llamadores
  donde un `None` no detectado corrompe datos); resto de llamadores = deuda.
- **Q5 = A**: **NEVER** incluir password/token del usuario en el mensaje, `repr` o `exc_info`
  de una excepción de integración (extiende las reglas afirmadas de no-credenciales-en-claro).
- **Q6 = A**: los `except: pass` de `data_manager_v2.py` (Intent 3) y `photo_service.py` quedan
  **FUERA de alcance** como deuda registrada; la primera oleada FR3.2 se mantiene en
  arranque/migraciones/`db_connection.py`/clientes + puntos de corrupción de `data_sync_service.py`.