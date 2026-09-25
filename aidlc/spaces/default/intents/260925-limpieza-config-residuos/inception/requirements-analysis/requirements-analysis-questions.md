# Requirements Analysis — Preguntas de aclaración

Intent: `260925-limpieza-config-residuos` (FR14 + FR15, scope `refactor`, Minimal).
Poda de bajo riesgo funcional, sin lógica nueva, characterization-first, coste 0 €.

Estas preguntas resuelven las decisiones de alcance que surgieron al escanear el
código real (ver `codekb/futmondo-analytics/code-quality-assessment.md`). Responde
cada una rellenando su `[Answer]:` con la letra elegida (o `X` + tu texto).

---

## Q1 — Retirada de las ramas de BD SQLite/Turso (FR14.1)

El escaneo confirma un dead-path SQLite/Turso completo y aislado en
`config.py` (cascada `DATABASE_URL → TURSO_DATABASE_URL → sqlite`) y
`db_connection.py` (`_init_turso`, `_TursoCursorWrapper`, `_init_sqlite`, ramas
`turso`/`sqlite` en `get_connection`/`adapt_sql`/`adapt_params`/`sync`), más
`libsql-experimental` en `requirements.txt`. Producción usa solo Neon
PostgreSQL. El fake de tests (`db_type="sqlite"` in-memory) está SEPARADO de la
rama SQLite de producción.

¿Qué alcance de retirada quieres?

- A. Retirar TODO el dead-path SQLite/Turso de producción (config + db_connection + `libsql-experimental`), caracterizando primero `db_connection.py` para garantizar que el contrato del cursor bajo Neon no cambia y que el fake de tests sigue verde.
- B. Retirar solo Turso (config cascade + `_init_turso`/`libsql-experimental`), conservando la rama SQLite de producción como fallback local documentado.
- C. Retirar solo lo huérfano de tooling (`nixpacks.toml`, scripts `migrate_*_to_turso`, `entrypoint.sh`) y dejar el código de BD intacto en este intent.
- D. No tocar código de BD; solo documentar la deuda.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Ficheros de tooling huérfanos: `entrypoint.sh`, `nixpacks.toml`, scripts de migración (FR14.1)

El escaneo indica: `nixpacks.toml` es config Railway/Nixpacks huérfana
(`python311` incoherente); `scripts/migrate_to_turso.py` y
`migrate_data_to_turso.py` no se usan en el flujo Neon; `entrypoint.sh` arranca
`cron` + uvicorn pero NO está referenciado por el Dockerfile ni por `fly.toml`
(candidato a residuo). El enunciado dice "tras confirmar que no se usan".

¿Cómo procedemos con estos ficheros?

- A. Eliminar los cuatro (`nixpacks.toml`, ambos `migrate_*_to_turso.py`, `entrypoint.sh`) tras verificar por grep/CI que no hay referencia viva.
- B. Eliminar los tres de Turso/Railway (`nixpacks.toml`, ambos scripts) pero CONSERVAR `entrypoint.sh` (revisarlo aparte por el arranque de `cron`).
- C. Eliminar solo los scripts `migrate_*_to_turso.py`; dejar `nixpacks.toml` y `entrypoint.sh`.
- D. No eliminar ninguno en este intent; registrarlos como deuda.
- X. Other (please specify)

[Answer]: A

---

## Q3 — IDs hardcodeados `CHAMPIONSHIP_ID` / `LEAGUE_ID` (FR14.2)

Corrección de trazabilidad del escaneo: estos defaults hardcodeados están en
`backend/app/core/config.py`, NO en `constants.py` como decía el enunciado del
backlog. Son residuo de la etapa mono-usuario en una app hoy
multi-usuario/multi-campeonato. `constants.py` solo tiene `LALIGA_TEAMS`
(fallback legítimo, no residuo).

¿Qué hacemos con los defaults hardcodeados en `config.py`?

- A. Eliminar los defaults hardcodeados de `config.py` (dejar el valor sin default u obligado por entorno), tras verificar que ningún path de producción depende de esos defaults (el flujo multi-usuario usa las credenciales/campeonatos del usuario logado).
- B. Mantener las variables pero neutralizar el default (a `None`/vacío) y que el código falle explícito si se usara sin configurar.
- C. Solo mover a variable de entorno documentada, conservando un default no sensible.
- D. No tocar; documentar como deuda.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Doble montaje de `matchdays` (FR15)

En `main.py` el mismo router se incluye dos veces: `prefix="/api/v1/matchdays"`
y `prefix="/v1/matchdays"` (comentario "avoid redirect loops"). El segundo
prefijo `/v1/matchdays` puede tener clientes legacy.

¿Cómo unificamos el montaje?

- A. Conservar solo `/api/v1/matchdays` (canónico) y retirar `/v1/matchdays`, PREVIA verificación de que ningún cliente (frontend Angular, crons Sofascore, proxy nginx) consume el segundo prefijo; si algún cliente lo usa, ajustarlo al canónico en el mismo intent.
- B. Conservar solo el canónico y retirar el segundo SIN verificación de clientes (asumir que no hay legacy).
- C. Mantener ambos pero dejar el segundo como redirect explícito al canónico (no doble include).
- D. No tocar el montaje en este intent; registrar la deuda.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Artefactos basura versionados (FR15)

El escaneo lista residuos no cubiertos por `.gitignore`: `*.jpg:Zone.Identifier`
(marcadores NTFS Windows), imágenes sueltas (`42874.jpg` ≈580 KB), directorios
`stitch_team_card_dashboard/` y `stitch_angular_material_card_redesign/`
(mockups ≈370 KB). Además `node_modules.old-*/` y `*.db` sí están en
`.gitignore` pero podrían estar trackeados históricamente.

¿Qué alcance de limpieza de residuos?

- A. `git rm` de todos los residuos listados (Zone.Identifier, imágenes sueltas, directorios `stitch_*`), y AÑADIR patrones a `.gitignore` para prevenir reincidencia (`*:Zone.Identifier`, `stitch_*/`); además `git rm --cached` de lo ya-ignorado pero trackeado (`node_modules.old-*/`, `*.db`) si el historial lo tiene vivo.
- B. Solo `git rm` de los residuos + endurecer `.gitignore`, sin tocar lo ya-ignorado aunque esté trackeado.
- C. Solo `git rm` de los residuos, sin cambios en `.gitignore`.
- D. No tocar; documentar la deuda.
- X. Other (please specify)

[Answer]: A

---

## Q6 — Comentarios obsoletos "Railway"/"Turso" (alcance de higiene)

El escaneo señala comentarios "Railway"/"Turso" obsoletos dispersos en
`config.py`, `db_connection.py`, `docker-compose.yml`. No son código muerto,
solo ruido documental.

¿Los limpiamos en este intent?

- A. Sí, retirar los comentarios obsoletos SOLO en los ficheros que ya vamos a tocar por FR14 (quirúrgico, sin reformateo masivo, respetando la regla de no `ruff format` masivo brownfield).
- B. Sí, retirarlos en todos los ficheros donde aparezcan aunque no los toquemos por FR14.
- C. No, dejarlos; fuera de alcance de esta poda.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones tomadas para la limpieza FR14+FR15 (todas con la
recomendación por defecto: retirada completa, con verificación previa y
characterization-first, coste 0 €):

- Q1 → A: Retirar TODO el dead-path SQLite/Turso de producción (`config.py` cascade, `db_connection.py` ramas `_init_turso`/`_TursoCursorWrapper`/`_init_sqlite`/`turso`/`sqlite`, y `libsql-experimental` en `requirements.txt`), caracterizando primero `db_connection.py` para no alterar el contrato del cursor bajo Neon y dejar el fake de tests verde.
- Q2 → A: Eliminar los cuatro huérfanos (`nixpacks.toml`, `scripts/migrate_to_turso.py`, `scripts/migrate_data_to_turso.py`, `entrypoint.sh`) tras verificar por grep/CI que no hay referencia viva (Dockerfile, `fly.toml`, workflows).
- Q3 → A: Eliminar los defaults hardcodeados `CHAMPIONSHIP_ID`/`LEAGUE_ID` de `backend/app/core/config.py` (no `constants.py`; corrección de trazabilidad del escaneo), tras verificar que ningún path de producción depende de ellos (flujo multi-usuario usa datos del usuario logado).
- Q4 → A: Conservar solo `/api/v1/matchdays` (canónico) y retirar `/v1/matchdays`, previa verificación de clientes (frontend Angular, crons Sofascore, proxy nginx); si algún cliente lo usa, ajustarlo al canónico en el mismo intent.
- Q5 → A: `git rm` de todos los residuos (`*:Zone.Identifier`, imágenes sueltas, directorios `stitch_*`) + endurecer `.gitignore` (`*:Zone.Identifier`, `stitch_*/`); además `git rm --cached` de lo ya-ignorado pero trackeado (`node_modules.old-*/`, `*.db`) si el historial lo tiene vivo.
- Q6 → A: Retirar comentarios obsoletos "Railway"/"Turso" solo en los ficheros que ya toquemos por FR14 (quirúrgico, sin `ruff format` masivo brownfield).

Restricciones transversales: sin lógica nueva, no ampliar god-files, gate de CI
bloqueante (gitleaks + pytest + ng test) en verde antes de merge, coste 0 €.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
