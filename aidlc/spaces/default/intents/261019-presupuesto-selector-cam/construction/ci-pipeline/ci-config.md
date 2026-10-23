# CI Config — F2

> Fase: construcción (ci-pipeline). Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA cambios de CI.** F2 añade código nativo iOS (`ios/`) que el CI actual no construye; no se añade runner Swift (coste 0 €, fuera de alcance — deuda aceptada ya registrada). El gate de CI bloqueante existente (`ci.yml` job `quality` + `fly-deploy.yml` job `verify`: gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`) **aplica al PR tal cual** y seguirá en verde porque F2 no toca backend ni frontend Angular.

## Qué corre en el PR de F2

- gitleaks escanea también los ficheros Swift nuevos (sin secretos).
- `pytest`/`ng test`/audits no se ven afectados (no hay cambios en backend/frontend).
- La verificación del código iOS (`swift build && swift test` + dispositivo) es **local/manual** (no en CI), como se acordó.

## Sources

- `aidlc/spaces/default/memory/team.md` (gate de CI durable)
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/infrastructure-design/cicd-pipeline.md`

## Assumptions & Open Questions

None.
