# Deployment Execution — Preguntas de clarificación

Intent: `sync-god-file` (Oleada 3, FR13) · scope `refactor` · fase Operation (última etapa).
El modelo de despliegue es **on-merge a `main`** hacia Fly.io: el deploy de producción
lo dispara `fly-deploy.yml` cuando los cambios aterrizan en `main` (vía PR squash-merge
tras el gate de CI bloqueante). Los cambios de este refactor están **sin commitear** en
el working tree (`main`); el deploy real aún no ha ocurrido.

---

## Q1 — Checks pre-despliegue

¿Cómo está la preparación pre-despliegue?

- A. **Todo listo para el release path**: suite en verde (251 passed, 3 xfailed), cobertura
  34.56% ≥ piso 27, `ruff check` limpio en ficheros nuevos, equivalencia estricta verificada
  (`git diff` byte-idéntico en el orquestador). Sin migraciones de BD (esquema no cambia).
  Servicios dependientes (Neon, Futmondo/Sofascore) sin cambios.
- B. Faltan checks por pasar antes de considerar el release.
- X. Other (please specify)

[Answer]: A (todo listo para el release path: suite 251 passed / 3 xfailed, cobertura 34.56% ≥ piso 27, ruff check limpio en ficheros nuevos, equivalencia estricta verificada por git diff, sin migraciones de BD, servicios dependientes sin cambios)

---

## Q2 — Ejecución del despliegue de producción

El deploy real a Fly.io se dispara on-merge a `main` y es un cambio en producción. ¿Qué hace
esta etapa respecto a la ejecución?

- A. **Documentar la preparación y el release path on-merge SIN ejecutar el deploy ni
  pushear a `main`** en esta sesión: el commit + PR + squash-merge (que dispara el gate de CI
  bloqueante y luego el deploy Fly.io) los realiza el humano cuando decida. Es la opción
  segura y alineada con las reglas afirmadas (nunca push directo a `main`; el gate de CI
  bloqueante debe pasar antes de fusionar).
- B. Que el agente commitee y abra el PR ahora (requiere tu confirmación explícita).
- C. Que el agente commitee, fusione a `main` y dispare el deploy de producción ahora
  (cambio en producción de alto riesgo; requiere tu confirmación explícita).
- X. Other (please specify)

[Answer]: A (documentar la preparación y el release path on-merge SIN ejecutar el deploy ni pushear a main en esta sesión; el commit + PR + squash-merge —que dispara el gate de CI bloqueante y luego el deploy Fly.io— los realiza el humano cuando decida)

---

## Consolidated Summary Confirmation

Resumen de las decisiones antes de generar los artefactos (última etapa):

- **Q1 — Checks pre-despliegue (A)**: todo listo. Suite backend 251 passed / 3 xfailed / 0 failed; cobertura 34.56% ≥ piso `--cov-fail-under=27`; `ruff check` limpio en los ficheros nuevos; equivalencia funcional estricta verificada por `git diff` (orquestador byte-idéntico); sin migraciones de BD (esquema no cambia); Neon y las integraciones Futmondo/Sofascore sin cambios.
- **Q2 — Ejecución (A)**: se documenta la preparación y el release path on-merge a `main` (Fly.io) SIN ejecutar el deploy ni pushear a `main` en esta sesión. El commit + PR + squash-merge (que dispara el gate de CI bloqueante `verify` y luego `deploy-backend` → `deploy-frontend` → `smoke-test`) los realiza el humano. Alineado con las reglas afirmadas: nunca push directo a `main`; un rojo nunca llega a producción; un deploy de producción es decisión humana.
- **Estado git actual**: rama `main`, cambios del refactor sin commitear (`data_sync_service.py` modificado; `backend/app/services/sync/` y `test_sync_match_odds_characterization.py` sin trackear). El deploy real ocurrirá on-merge, fuera de esta sesión.
- **Artefactos a generar**: `deployment-log.md` (preparación + release path, sin deploy ejecutado), `smoke-test-results.md` (el smoke test `/health` como verificación de release documentada, pendiente de ejecución on-merge), `health-check-report.md` (readiness contra `/health`, adaptado al stack Fly.io + Neon).

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
