# Reglas Descubiertas — 260918-matchday-prizes-calc

> Solo **constraints duros ya establecidos** (afirmados en intents previos o
> exigidos por el código/CI real). No se inventan reglas nuevas: la interview
> (completada, Q1-Q6) y el gate de afirmación deciden qué se promociona. Formato:
> `ALWAYS ...` / `NEVER ...`.

## Mandated

- ALWAYS mantener el proyecto a **coste 0 €**: descartar toda mejora o dependencia con
  gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free
  allowance, GitHub Actions free).
- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `pytest` + `ng test`) antes de
  fusionar a `main`; un rojo nunca llega a producción.
- ALWAYS **caracterizar (congelar con tests) el comportamiento de `sync_prizes` en TODAS
  sus ramas antes de refactorizarlo** hacia la mejora del cálculo de premios
  (characterization-first, Q2=A): `points_prize`, gating `round_fully_played`, ranking
  flop/top, MVP, dream-team, jornada adelantada/negativa y el borrado defensivo
  `DELETE ... NOT IN`. Hoy la producción del premio tiene cobertura directa cero. Extiende a
  este intent el mandato ya afirmado de characterization-first para `SessionStore`/`TaskManager`.
- ALWAYS exigir un `JWT_SECRET` **no-default** en el arranque del servicio web (NFR1.1;
  endurecido en `test_jwt_startup.py`).

## Forbidden

- NEVER almacenar la contraseña Futmondo en claro: ni en memoria ni en base de datos.
- NEVER usar un `JWT_SECRET` por defecto en producción.
- NEVER ampliar los god-files existentes (`data_sync_service.py` ~84 KB,
  `data_manager_v2.py` ~166 KB) ni el patrón SQL-en-router al tocar el cálculo de premios;
  el código nuevo va tras una capa/función estrecha testeable.
- NEVER correr `ruff format` masivo sobre archivos brownfield ya modificados (infla diffs,
  expone avisos preexistentes e invalida el pase de revisión en vuelo); formatear solo los
  archivos nuevos o de forma quirúrgica.
