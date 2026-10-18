**Collaborator:** aidlc-developer-agent

## Contribution

Revisión independiente (ciega) del borrador lead desde la óptica de
convenciones de código: nombres, fronteras de capa, manejo de errores,
organización de ficheros y estilo. El intent es un **análisis de viabilidad**
(Angular Native / NativeScript) cuyos entregables son documentos, no código de
aplicación, así que el criterio rector es: capturar la **línea base durable** y
NO arrastrar reglas de intents de refactor/CI que no tienen efecto sobre prosa.

### Convenciones durables — correctamente capturadas

- **Idioma del código (English identifiers / Castellano user-text + commits)**:
  bien capturado y además bien instanciado para un intent de análisis — la prosa
  de los documentos es texto de cara al usuario → castellano, con los nombres de
  framework (`NativeScript`, `Angular`, `FastAPI`), rutas, claves/enums YAML y
  tokens preservados verbatim en inglés. Es coherente con la regla afirmada en
  `team.md`/`project.md` y es la única parte de "Code Style" que **sí** aplica
  directamente a este intent (porque los entregables son prosa). Correcto.
- **No `ruff format` masivo sobre brownfield / no `--fix` de repo entero**: bien
  conservado como línea base durable. Para un intent de análisis es casi vacío
  (no se toca código), pero mantenerlo documentado es correcto y barato; evita
  que un futuro paso de implementación lo pierda.
- **Trunk-based + squash-merge + Conventional Commits (scope en castellano)**:
  correctamente recogido como línea base durable y correctamente matizado — las
  ramas/commits de documentación siguen la misma política y el gate de CI aplica
  igual aunque el cambio sea sólo documental. El añadido del prefijo `docs/...`
  y el scope `docs(feasibility)` es un refinamiento razonable y consistente con
  el patrón `tipo(scope)` existente.

### Reglas intent-específicas — correctamente NO arrastradas

- **God-files (`data_manager_v2.py`, `data_sync_service.py`,
  `assistant_service.py`, `photo_service.py`) — no ampliar/reescribir**: el
  borrador acierta al tratarlas como reglas de intents de refactor y dejarlas
  fuera. Un intent de análisis no modifica `backend/app/services/`, luego la
  prohibición no tiene superficie de aplicación. La evidencia de `code-structure.md`
  (god-files + `per-file-ignores` en `ruff.toml`) respalda que es estado del
  repo, no una obligación de este intent.
- **Characterization-first y excepciones tipadas / `return None` silencioso /
  no tragar fallos que corrompan datos**: correctamente NO carried forward. Son
  reglas de manejo de errores backend ligadas a intents que tocaban
  `_make_request`, `sync_prizes`, `SessionStore`/`TaskManager`. No hay código que
  caracterizar ni contrato de integración que cambiar en un documento de
  viabilidad. La asunción #2 de `evidence.md` lo deja explícito y marcado "A
  confirmar" en la entrevista — manejo correcto.
- **Pisos de cobertura concretos y promoción advisory→bloqueante / allowlist /
  pin de tooling del gate (FR11/FR12/FR17.3)**: bien excluidos como trabajo de
  los intents de CI gate-hardening. El borrador los menciona sólo como "estado
  heredado que este intent no modifica", que es la caracterización correcta.

### Fronteras de capa — un acierto a reforzar (señalamiento, no objeción)

El borrador y la evidencia capturan algo valioso para la ruta de implementación
nativa: la **clasificación portable vs no-portable** de `code-structure.md`
(`core/services/*` + `core/models/*` ≈ 1:1 portables; `features/*` + `shared/*`
atados a DOM/Material/plantillas HTML no portables) y la decisión de
arquitectura "backend como capa de dominio reutilizable → migrar a nativo es
reemplazo de la capa de presentación, no un rewrite del backend". Esto es, de
hecho, la convención de **frontera de capa** más relevante para este intent y
está bien reflejada en `architecture.md`; sugiero que la integración final la
suba de la evidencia al cuerpo del análisis como criterio de diseño, no sólo
como nota de evidencia.

### Imprecisión menor a corregir (manejo de errores / estado del gate)

En `team-practices.md` (Code Style) y en `discovered-rules.md` se afirma que
`ruff check` es **bloqueante en ambos gates**. El `backend/ruff.toml` que leí
sigue documentando en su cabecera el modo **advisory** (`continue-on-error`,
"se pasará a bloqueante en un trabajo posterior"). La evidencia (`evidence.md`,
fila `ci.yml`) sí registra `ruff ==0.16.9 bloqueante`, por lo que el estado real
del repo probablemente evolucionó más allá del comentario del `.toml`. No es un
error de arrastre, pero el comentario de cabecera de `ruff.toml` quedó **stale**
y puede inducir a confusión en un lector futuro. Recomiendo (a) que la redacción
del borrador cite la fuente de verdad del estado del gate (`ci.yml`), y (b)
anotar el comentario stale de `ruff.toml` como deuda de documentación — sin
tocar el fichero en este intent de análisis.

### Organización de ficheros / entregables

La ubicación de los entregables (documentos de análisis bajo el record del
intent) y la no-creación de árboles de tests o código nuevo es coherente con un
intent `classic` de análisis. No hay observaciones de organización que objetar.

## Positions

AGREE: Las convenciones durables (idioma English/Castellano, no `ruff format` masivo brownfield, trunk-based + squash-merge + Conventional Commits) están correctamente capturadas y bien matizadas para un intent de prosa.
AGREE: Las reglas de god-files, characterization-first, excepciones tipadas y CI gate-hardening están correctamente NO arrastradas; carecen de superficie de aplicación en un intent de análisis.
AGREE: Tratar coste 0 € y "no credenciales en claro" como reglas durables de seguridad relevantes al riesgo de portabilidad del modelo de sesión nativo es la decisión correcta.
OBJECT: La afirmación "`ruff check` bloqueante en ambos gates" debería anclarse a `ci.yml` (fuente de verdad) y señalar que el comentario de cabecera de `backend/ruff.toml` quedó stale (aún dice advisory) — precisión, no cambio de alcance.
OBJECT: La frontera de capa portable/no-portable (`core/services`+`models` portables; `features`+`shared` no portables) y "migrar nativo = reemplazo de presentación, no rewrite del backend" merecen subir de la evidencia al cuerpo del análisis como criterio de diseño, no quedar sólo como nota de evidencia.
