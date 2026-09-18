# AI-DLC — Parche local en 2.9.0 (fix propio de summary-authorization)

> **Estado**: parche local activo sobre AI-DLC **2.9.0**.
> **Fecha**: 2026-09-18.
> **Alcance**: este proyecto (`futmondo-analytics`). No modifica el binario ni la
> instalación global; solo el árbol de herramientas versionado en `.kiro/`.

## Qué saber al arrancar un nuevo intent

Este proyecto corre AI-DLC 2.9.0 con un **parche local** en
`.kiro/tools/aidlc-lib.ts`. Cualquier intent nuevo lo hereda automáticamente
(el hook lo lee de `.kiro/` en tiempo de ejecución). **No hace falta hacer nada
especial** para beneficiarse del fix; solo hay que saber que existe para:

- No sorprenderse de que `.kiro/tools/aidlc-lib.ts` difiera del framework oficial.
- **Revertirlo** cuando salga una versión oficial (> 2.9.0) que incluya el arreglo.

## El bug que corrige

En AI-DLC 2.9.0, las etapas con `summary_confirmation` (p. ej. las de fase
Operation) podían quedar **bloqueadas en el gate** con el error
`SUMMARY_ARTIFACT_UNAUTHORIZED` ("output document ... was last saved before the
confirmed answers"), aun habiendo confirmado el resumen y regenerado los
artefactos.

### Causa raíz

- El hook `aidlc-write-audit-log` estampa el campo `Summary Authorization Id` en
  las filas `ARTIFACT_UPDATED`/`ARTIFACT_CREATED` leyendo la confirmación activa
  vía `readSummaryAuthorization()` en `.kiro/tools/aidlc-lib.ts`.
- Esa función elegía entre el árbol nuevo
  (`<record>/.aidlc-engine/summary-authorization/`) y el legacy
  (`<record>/.aidlc-summary-authorization/`) mediante `engineReadDirFor()`, que
  decide **por existencia del directorio raíz del registro**, no por el fichero
  concreto de la etapa.
- Si la confirmación de una etapa se escribía en el árbol **legacy** mientras el
  árbol **nuevo** ya existía (por etapas anteriores), la función nunca
  encontraba la confirmación → el hook no estampaba el id → el guard del gate
  interpretaba los artefactos como "guardados antes de la confirmación" y
  rechazaba.
- Detalle de arquitectura relevante: el binario `aidlc` (autocontenido, ELF)
  **carga los hooks desde los `.ts` de `.kiro/` del proyecto** en tiempo de
  ejecución (`resolveHookPath` → `import()` dinámico), no desde código embebido.
  Por eso el fix correcto es parchear el `.ts` del proyecto, no recompilar el
  binario.

## El parche

Fichero: `.kiro/tools/aidlc-lib.ts`, función `readSummaryAuthorization()`.

En lugar de elegir el árbol por el directorio raíz, ahora se prueba el fichero
del árbol nuevo y, si no existe, se cae al fichero del árbol legacy
**por-fichero**:

```ts
const relativePath = summaryAuthorizationRelativePath(stage, unit);
const legacyRelativePath = `${LEGACY_SUMMARY_AUTHORIZATION_DIR}${relativePath.slice(SUMMARY_AUTHORIZATION_DIR.length)}`;
const enginePath = recordFileTargetOrThrow(record, relativePath);
const legacyPath = recordFileTargetOrThrow(record, legacyRelativePath);
// Prefiere el árbol nuevo; cae al legacy POR FICHERO (no por directorio raíz).
const path = existsSync(enginePath) ? enginePath : legacyPath;
```

No cambia el comportamiento cuando el fichero nuevo existe (preferencia por el
nuevo intacta); solo añade el fallback por-fichero que faltaba. No toca escritura
de confirmaciones, ni el guard, ni el estado del workflow.

## Verificación

- `aidlc doctor` → **0 problemas** (binario original intacto; solo cambia un
  fichero versionado de `.kiro/`, que el inventario de integridad no cubre).
- Con el parche, el hook estampa `Summary Authorization Id` en las filas de
  artefacto y los gates de summary-confirmation abren con normalidad.
- Validado de punta a punta en las etapas `deployment-pipeline` y
  `deployment-execution` del intent `260916-backend-security-hardeni`.

## Origen del fix y cómo revertir

- El parche se derivó del repositorio fuente del framework
  (`aidlc-workflows`, tag `v2.9.0`); a fecha de hoy `main` upstream **aún no**
  incluye este arreglo (`engineReadDirFor`/`readSummaryAuthorization` sin
  cambios respecto a 2.9.0).
- **Al actualizar** a una versión oficial que incluya el fix: revertir este
  parche local (restaurar `readSummaryAuthorization` a la versión oficial) para
  no arrastrar una divergencia innecesaria. Un `aidlc config`/actualización que
  redepliegue los `.kiro/tools/` **sobrescribirá** este parche; si eso ocurre
  antes del fix oficial, habrá que reaplicarlo.

## Backups locales (fuera de git)

- `~/.local/share/aidlc/versions/2.9.0/aidlc.orig-2.9.0.bak`: copia del binario
  2.9.0 original (red de seguridad; el binario en uso es el original sin
  modificar).
