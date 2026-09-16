# Reglas descubiertas — Futmondo Analytics

> Versión integrada por el lead (aidlc-pipeline-deploy-agent). Solo **restricciones
> duras** afirmadas por el humano en la entrevista o ya vigentes en `project.md`. Las
> señales de deuda de las contribuciones (p. ej. `except Exception: pass`, bug de
> precedencia, `NODE_TLS_REJECT_UNAUTHORIZED=0`) NO son reglas afirmadas: quedan como
> evidencia/tradeoffs en `evidence.md`.

## Mandated

- ALWAYS mantener el proyecto a coste 0 €: descartar toda mejora o dependencia con
  gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free,
  Fly.io free allowance, GitHub Actions free). (ya afirmada en `project.md`)
- ALWAYS pasar el gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de
  fusionar a `main`; un rojo nunca llega a producción.
- ALWAYS caracterizar (congelar con tests) el comportamiento de `SessionStore` y
  `TaskManager` antes de refactorizarlos hacia durabilidad (characterization-first;
  hoy no tienen cobertura directa).

## Forbidden

- NEVER almacenar la contraseña Futmondo en claro: ni en memoria (deuda actual de
  `UserSession`, FR5) ni en la base de datos al diseñar la durabilidad. (El orden de
  preferencia entre re-autenticación y cifrado en reposo se decide en diseño, no aquí.)
- NEVER usar un `JWT_SECRET` por defecto en producción; el arranque del servicio web
  exige un secreto no-default (NFR1.1; endurecido en `test_jwt_startup.py`).

## Sources

- `practices-discovery-questions.md` (Q3 characterization-first, Q5 prohibición dura FR5).
- `aidlc/spaces/default/memory/project.md` (`## Corrections`: coste 0 €).
- `aidlc/spaces/default/codekb/futmondo-analytics/code-quality-assessment.md`
  (estado en memoria no durable FR1, credenciales en claro FR5, guard JWT NFR1.1,
  characterization-first).
- `.github/workflows/ci.yml` (gitleaks/pytest/ng test bloqueantes; `JWT_SECRET`
  requerido en CI).
- `.github/workflows/fly-deploy.yml` (re-verify + smoke test `/health`).
