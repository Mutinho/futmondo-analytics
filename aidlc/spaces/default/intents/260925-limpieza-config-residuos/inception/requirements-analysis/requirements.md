# Requisitos — Limpieza de configuración y residuos (FR14 + FR15)

Intent: `260925-limpieza-config-residuos` · Scope: `refactor` (Minimal) · Proyecto: brownfield (Futmondo Analytics).
Origen: `docs/BACKLOG-plan-intents.md` (Intent 2), plan de análisis `260911-analisis-mejoras` (FR14, FR15).

## Análisis de intención

El objetivo es **reducir ruido y superficie de mantenimiento** eliminando
configuración y código muertos y artefactos basura versionados, **sin introducir
lógica nueva ni cambiar el comportamiento en producción**. Producción corre solo
sobre Neon PostgreSQL (Fly.io), por lo que las ramas SQLite/Turso y el tooling
Railway son dead-path. La app es hoy multi-usuario/multi-campeonato, por lo que
los IDs hardcodeados de la etapa mono-usuario son residuo. Toda intervención es
de **bajo riesgo funcional**, guiada por **characterization-first** donde toque
código con contrato (el motor de BD), y verificada por el gate de CI bloqueante
antes de fusionar. Restricción dura: **coste 0 €** (solo tiers gratuitos).

## Requisitos funcionales

### FR14 — Limpieza de configuración de base de datos e IDs hardcodeados

**FR14.1 — Retirar el dead-path SQLite/Turso de producción**
El sistema shall usar **exclusivamente Neon PostgreSQL** como motor de BD en el
código de producción, eliminando las ramas muertas SQLite/Turso.
- FR14.1.1 — Eliminar de `backend/app/core/config.py` la resolución en cascada
  `DATABASE_URL → TURSO_DATABASE_URL → sqlite` y las variables Turso
  (`TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`) y `POSTGRES_*` manuales que solo
  sirven al dead-path.
- FR14.1.2 — Eliminar de `backend/app/services/db_connection.py` las ramas
  `turso`/`sqlite` de producción: `_init_turso`, `_TursoCursorWrapper`,
  `_init_sqlite`, y las ramas correspondientes en `get_connection`,
  `adapt_sql`, `adapt_params`, `get_last_insert_id` y `sync`.
- FR14.1.3 — Eliminar `libsql-experimental==0.0.55` de `requirements.txt` tras
  confirmar que no queda ningún import vivo al retirar `_init_turso`.
- FR14.1.4 — Eliminar los ficheros de tooling huérfano tras verificar por
  búsqueda/CI que no hay referencia viva (Dockerfile, `fly.toml`, workflows):
  `nixpacks.toml`, `backend/scripts/migrate_to_turso.py`,
  `backend/scripts/migrate_data_to_turso.py` y `entrypoint.sh`.
- FR14.1.5 — **Characterization-first**: antes de modificar `db_connection.py`,
  congelar con tests el contrato del cursor/`adapt_sql`/`adapt_params` bajo el
  path Neon PostgreSQL, garantizando que ningún llamador dependa del
  comportamiento SQLite (`?` placeholders) y que el fake de tests in-memory
  (`db_type="sqlite"` en `conftest.py`/`test_db_engine_characterization.py`),
  que es independiente de la rama SQLite de producción, permanece verde tras la
  retirada.
- FR14.1.6 — Retirar los comentarios obsoletos "Railway"/"Turso" **solo** en
  los ficheros ya tocados por FR14 (higiene quirúrgica; sin reformateo masivo).

**FR14.2 — Eliminar IDs hardcodeados de campeonato/liga**
El sistema shall no depender de identificadores de campeonato/liga hardcodeados.
- FR14.2.1 — Eliminar los defaults hardcodeados `CHAMPIONSHIP_ID` y `LEAGUE_ID`
  de **`backend/app/core/config.py`** (corrección de trazabilidad: el enunciado
  del backlog nombraba `constants.py`, pero el escaneo confirma que están en
  `config.py`; `constants.py` solo tiene `LALIGA_TEAMS`, fallback legítimo, que
  NO se toca).
- FR14.2.2 — Verificar que ningún path de producción depende de esos defaults
  (el flujo multi-usuario usa credenciales/campeonatos del usuario logado) antes
  de retirarlos; el código shall fallar de forma explícita si se usara sin
  configurar, en vez de asumir un default silencioso.

### FR15 — Unificación de rutas y eliminación de artefactos basura

**FR15.1 — Unificar el doble montaje de `matchdays`**
- FR15.1.1 — En `backend/app/main.py`, conservar solo el prefijo canónico
  `/api/v1/matchdays` y retirar el segundo montaje `/v1/matchdays`.
- FR15.1.2 — Verificar antes de retirar que ningún cliente consume
  `/v1/matchdays` (frontend Angular, crons Sofascore, proxy nginx); si algún
  cliente lo usa, ajustarlo al prefijo canónico dentro de este mismo intent.

**FR15.2 — Sacar del control de versiones los artefactos basura**
- FR15.2.1 — `git rm` de los residuos versionados: marcadores NTFS
  `*.jpg:Zone.Identifier` (`42874.jpg:Zone.Identifier`,
  `30825.jpg:Zone.Identifier`, `IMG_9904.PNG:Zone.Identifier`), imágenes sueltas
  (p. ej. `42874.jpg`), y los directorios de mockups
  `stitch_team_card_dashboard/` y `stitch_angular_material_card_redesign/`.
- FR15.2.2 — Endurecer `.gitignore` para prevenir reincidencia, añadiendo al
  menos `*:Zone.Identifier` y `stitch_*/`.
- FR15.2.3 — `git rm --cached` de lo cubierto por `.gitignore` pero trackeado
  históricamente si el historial lo tiene vivo: `node_modules.old-*/` y
  `backend/futmondo_data.db` (`*.db`).

## Requisitos no funcionales

- NFR1 — **Preservación de comportamiento**: la suite de tests existente
  (backend `pytest` + frontend `ng test`) shall permanecer en verde tras cada
  cambio; ninguna retirada introduce regresión funcional observable.
- NFR2 — **Gate de CI bloqueante**: los cambios shall pasar el gate bloqueante
  (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`.
- NFR3 — **Coste 0 €**: ninguna dependencia o servicio con gasto recurrente; la
  retirada de `libsql-experimental` reduce superficie sin coste.
- NFR4 — **Diffs mínimos y revisables**: sin `ruff format`/Prettier masivo sobre
  brownfield; cambios quirúrgicos y aislados por commit (p. ej. la config de BD
  separada de la limpieza de residuos y de la ruta `matchdays`).

## Restricciones

- C1 — **Sin lógica nueva**: es una poda; no se añaden features ni se altera el
  flujo de negocio.
- C2 — **No ampliar god-files** (`data_manager_v2.py`, `data_sync_service.py`,
  `assistant_service.py`) ni el patrón SQL-en-router (regla afirmada).
- C3 — **Characterization-first** obligatorio antes de tocar `db_connection.py`.
- C4 — Convenciones del proyecto: identificadores/comentarios en inglés, prosa
  de usuario y mensajes de commit en castellano; Conventional Commits con scope.
- C5 — Tests con dobles/fakes en memoria; sin red, sin BD real, sin credenciales.

## Supuestos

- A1 — Producción no usa SQLite ni Turso; Neon PostgreSQL es el único motor
  activo (evidencia: `README.md`, `team.md` Deployment, escaneo de codeKB). A
  validar en la verificación de FR14.1 antes de borrar.
- A2 — El fake de tests SQLite in-memory es independiente de la rama SQLite de
  producción y sobrevive a su retirada (evidencia: escaneo; a confirmar con la
  caracterización FR14.1.5).
- A3 — `entrypoint.sh` no está referenciado por el arranque real (Dockerfile/
  `fly.toml`); su función de `cron` la cubren los crons Fly.io one-shot. A
  validar por búsqueda antes de borrar (FR14.1.4).
- A4 — El flujo multi-usuario no depende de `CHAMPIONSHIP_ID`/`LEAGUE_ID`
  hardcodeados. A validar antes de retirarlos (FR14.2.2).

## Fuera de alcance

- OOS1 — Descomposición de god-files (FR13, Intent 3 del backlog).
- OOS2 — Endurecimiento del gate CI/CD: pisos de cobertura, promover linters a
  bloqueante, paridad `--cov` en `verify` (FR11/FR12/FR17.3, Intent 4).
- OOS3 — Cualquier cambio de comportamiento funcional, nuevo endpoint o feature.
- OOS4 — Retirada de comentarios obsoletos en ficheros NO tocados por FR14
  (Q6 acotó la higiene a los ficheros ya intervenidos).
- OOS5 — Reescritura del pinning de dependencias backend con rango abierto
  (deuda registrada, no de esta poda).

## Preguntas abiertas

- OQ1 — Confirmar en construcción el inventario exacto de clientes de
  `/v1/matchdays` (si resultara haber alguno, se ajusta al canónico; no se
  prevé, pero la verificación FR15.1.2 lo cierra).
- OQ2 — Confirmar por historial de git qué residuos ya-ignorados
  (`node_modules.old-*/`, `*.db`) están realmente trackeados y requieren
  `git rm --cached` (FR15.2.3).

## Sources

- `docs/BACKLOG-plan-intents.md` — Intent 2 (FR14 + FR15) y restricciones transversales.
- `aidlc/spaces/default/codekb/futmondo-analytics/code-quality-assessment.md` — deuda FR14/FR15 con evidencia por fichero (foco del intent).
- `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md`, `code-structure.md`, `business-overview.md` — arquitectura, estructura y dominio.
- `aidlc/spaces/default/intents/260925-limpieza-config-residuos/project-description.json` — descripción autoritativa del intent.
- `aidlc/spaces/default/intents/260925-limpieza-config-residuos/inception/requirements-analysis/requirements-analysis-questions.md` — decisiones de alcance Q1-Q6 (todas A).
- `aidlc/spaces/default/memory/{team,project}.md` — prácticas afirmadas (coste 0 €, gate CI, characterization-first, no ampliar god-files, no reformateo masivo).

## Assumptions & Open Questions

Ver secciones "Supuestos" (A1-A4) y "Preguntas abiertas" (OQ1-OQ2) arriba. Ninguna bloquea la generación; todas se cierran con verificaciones acotadas en construcción antes de cada retirada.
