# Practices Discovery — Entrevista

Re-run brownfield. Las prácticas base ya están afirmadas (Way of Working,
Walking Skeleton OFF, Testing Posture test-after, Deployment on-merge Fly.io,
Code Style). Solo se pregunta lo que la revisión ciega dejó sin resolver para
este intent de fiabilidad.

## Q1. Floor de aserción significativa para specs de modos de fallo

La revisión de calidad advierte: un spec que solo hace `pytest.raises(...)` sin aservar el *efecto* replicaría la brecha de significatividad (como la de FR17.1 en frontend). ¿Fijamos un floor explícito?

- A. **Sí, floor explícito**: cada spec de manejo de error debe aservar el efecto, no solo que se lanza/captura. Para recuperable: paso marcado `DEGRADED` y la operación NO falla. Para fatal: excepción tipada propagada Y no hay datos a medias escritos. Nada de `pytest.raises` sin aserción de estado.
- B. No hace falta floor explícito; basta la posture test-after actual.
- X. Other (please specify)

[Answer]: A. Sí, floor explícito: cada spec de manejo de error asvera el efecto (recuperable → paso DEGRADED y la operación no falla; fatal → excepción tipada propagada y sin datos a medias). Nada de pytest.raises sin aserción de estado.

## Q2. Enforcement de bare-except (`E722`)

`E722` está hoy en `ignore` de `ruff.toml` y `ruff check` es advisory (no bloquea). ¿Qué hacemos con el enforcement de bare-except en este intent?

- A. **Re-habilitar `E722` como advisory** (trinquete): quitarlo de `ignore` para que `ruff check` lo reporte, sin promover ruff a bloqueante todavía. Aísla el reflow (solo la regla, sin reformateo masivo).
- B. **Re-habilitar `E722` Y hacerlo bloqueante** para bare-except nuevos en las zonas tocadas.
- C. **Diferir**: dejar el enforcement de bare-except fuera de este intent; solo endurecer manualmente las capturas de la primera oleada.
- X. Other (please specify)

[Answer]: A. Re-habilitar E722 como advisory (trinquete): quitarlo de ignore para que ruff check lo reporte, sin promover ruff a bloqueante; aislar el reflow.

## Q3. Dónde vive la jerarquía de excepciones tipadas de integración

El developer señala que "extender `SofascoreIPBanError`" deja acoplamiento implícito (esa clase vive dentro del cliente Sofascore). Propone un módulo dedicado.

- A. **Módulo dedicado `integration_errors`** con una raíz común `IntegrationError` y subtipos por modo de fallo (baneo, timeout, respuesta no parseable), del que hereden tanto Sofascore como Futmondo. Módulo estrecho y testeable, fuera de los god-files.
- B. **Cada cliente define las suyas** (sin raíz común): Futmondo replica el patrón de Sofascore en su propio fichero.
- C. Not yet defined (que lo decida functional-design).
- X. Other (please specify)

[Answer]: A. Módulo dedicado integration_errors con raíz común IntegrationError y subtipos por modo de fallo, del que hereden Sofascore y Futmondo; capa estrecha y testeable fuera de los god-files.

## Q4. Alcance del cambio de contrato de `futmondo_client` (FR4)

Cambiar `_make_request` de `None`-como-fallo a excepciones tipadas afecta a muchos llamadores del god-file de sync que asumen `None == sin datos`. ¿Hasta dónde llega la migración en este intent?

- A. **Caracterizar primero, migrar los puntos de corrupción + `_make_request`**: mapear los llamadores (inventario verificable como entregable), caracterizar su comportamiento actual, y migrar el núcleo (`_make_request` + los llamadores donde un `None` no detectado corrompe datos); el resto de llamadores queda como deuda.
- B. **Migrar todos los llamadores** (`sync_*`/`get_*`) en este intent.
- C. **Solo `_make_request`**, dejando los llamadores adaptándose por compatibilidad (excepción capturada y traducida en un punto).
- X. Other (please specify)

[Answer]: A. Caracterizar primero; migrar los puntos de corrupción + _make_request, con el inventario de llamadores como entregable verificable; el resto de llamadores queda como deuda.

## Q5. Regla de seguridad: excepciones de integración sin secretos

DevSecOps advierte que el hardening de FR4 roza el manejo de credenciales. ¿Añadimos una regla dura?

- A. **Sí (NEVER)**: la excepción tipada de `futmondo_client` NUNCA incluye password/token del usuario en su mensaje, `repr` o `exc_info`. (Complementa las reglas ya afirmadas de no-credenciales-en-claro.)
- B. No hace falta regla explícita; basta con la práctica general.
- X. Other (please specify)

[Answer]: A. Sí (NEVER): la excepción tipada de futmondo_client nunca incluye password/token del usuario en su mensaje, repr o exc_info.

## Q6. `except: pass` de `data_manager_v2.py` / `photo_service.py`

El scope-document excluyó las 29 capturas de `data_sync_service.py` (salvo corrupción). Los 3 `except: pass` reales de `data_manager_v2.py` y el de `photo_service.py` (solo skimmed en RE) no se clasificaron explícitamente.

- A. **Fuera de alcance**: `data_manager_v2.py` es god-file (Intent 3) y `photo_service.py` no es zona de fiabilidad de este intent; quedan como deuda registrada. La primera oleada se mantiene en arranque/migraciones/`db_connection.py`/clientes + puntos de corrupción de `data_sync_service.py`.
- B. **Incluir los `except: pass`** de esos ficheros en la primera oleada (requiere análisis profundo previo de los god-files skimmed).
- X. Other (please specify)

[Answer]: A. Fuera de alcance: data_manager_v2.py (Intent 3) y photo_service.py como deuda registrada; la primera oleada se mantiene en arranque/migraciones/db_connection.py/clientes + puntos de corrupción de data_sync_service.py.

## Consolidated Summary Confirmation

Resumen de las prácticas de este intent (re-run; base afirmada preservada, más las precisiones de la entrevista):

- **Way of Working / Deployment / Walking Skeleton**: sin cambios respecto a lo afirmado (trunk-based squash-merge, on-merge Fly.io, walking skeleton OFF).
- **Testing Posture**: test-after; orden = characterization-first de cada captura tocada y del contrato de `_make_request` (con inventario de llamadores) → implementación de excepciones tipadas → specs que aseveran el EFECTO (recuperable→`DEGRADED`+no falla; fatal→propaga+sin datos a medias); nada de `pytest.raises` sin aserción (Q1). `--cov` observabilidad-only; asimetría `ci.yml`/`verify` diferida.
- **Code Style**: módulo `integration_errors` con raíz `IntegrationError` (Q3); mensajes de excepción en inglés / texto usuario en castellano; `E722` re-habilitado ADVISORY por trinquete, reflow aislado (Q2); no reformateo masivo.
- **Mandated (+)**: caracterizar llamadores + inventario antes del cambio de contrato (Q4); aseverar el efecto en specs de fallo (Q1).
- **Forbidden (+)**: no traer al alcance los `except: pass` de `data_manager_v2.py`/`photo_service.py` (Q6); nunca password/token en mensaje/`repr`/`exc_info` de excepción de integración (Q5).
- **Artefactos**: team-practices.md, discovered-rules.md, evidence.md, practices-discovery-timestamp.md.

[Answer]: Looks correct
