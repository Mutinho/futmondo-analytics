# Deployment Execution — Preguntas (Intent 4: gate CI/CD hardening)

> Etapa terminal de despliegue de este intent config-only. **No hay código de
> aplicación nuevo que desplegar**: el "despliegue" de este intent es el push a
> `main` de los commits `chore(ci)` que endurecen el gate; el CD de la app
> (`deploy-backend`/`deploy-frontend`) se dispara igual que siempre. `build-test-results`
> ausente (scope infra omite build-and-test). Estas preguntas cierran el encuadre
> de los artefactos de ejecución.

---

## Q1 — Naturaleza del despliegue de este intent

¿Qué "despliega" esta etapa?

- A. **Config del gate vía commits `chore(ci)` a `main`**: no hay artefacto de
  aplicación nuevo; el cambio son los workflows/config (`ci.yml`,
  `fly-deploy.yml`, `pytest.ini`, `angular.json`, `requirements.txt`, allowlist +
  script). Documentar el LOG de despliegue como **procedimiento y estado
  esperado** de esos commits (secuencia escalonada, verde en ambos gates), sin
  fabricar un push real que aún no se ha ejecutado.
- B. Un despliegue de aplicación (código nuevo).
- X. Other (please specify)

[Answer]: A

---

## Q2 — Migraciones de base de datos

¿Requiere este intent migraciones de BD?

- A. **Ninguna**: el intent es config-only de CI/CD; no toca esquema ni datos de
  Neon. No se delega ejecución de migración al developer.
- B. Sí, hay migraciones que ejecutar.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Smoke test y health check (qué se documenta)

¿Cómo se documentan `smoke-test-results.md` y `health-check-report.md` para un
intent que no cambia el runtime?

- A. **Comportamiento esperado del smoke test/health check existentes**: el
  `smoke-test` `/health` (5 reintentos, HTTP 200) y los healthchecks (`/health`,
  `/`) son los ya operativos; como el intent no cambia el runtime, el resultado
  esperado del deploy de los `chore(ci)` es idéntico al de la línea base (verde).
  Documentar el criterio y el estado esperado, marcando que la verificación real
  ocurre al pushear cada commit. Sin inventar resultados de una ejecución que no
  se ha hecho.
- B. Documentar resultados de una ejecución de deploy real.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Ventana de despliegue y secuenciación

¿Cómo se documenta la ventana/secuencia de despliegue de los commits `chore(ci)`?

- A. **Secuencia escalonada, cada commit verificado en verde antes del
  siguiente**: los 8 commits `chore(ci)` se pushean en orden (gitleaks unificado
  → pins → allowlist+expiry → pip-audit → npm audit → ruff → piso+paridad →
  ratchet frontend); cada uno debe pasar el gate (PR + `verify`) en verde antes
  de continuar; rollback quirúrgico por commit si uno rompe. Sin ventana de
  freeze especial (single-maintainer, deploy on-merge).
- B. Un único big-bang de todos los cambios a la vez.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Pre-deployment checks

¿Qué checks previos se documentan antes de pushear cada `chore(ci)`?

- A. **Checks previos a coste 0 €**: (i) reproducir el gate en local antes de
  pushear cambios de tooling/pins (venv efímero para pytest, contenedor
  `node:22.22.3` para `ng test` si se tocara el frontend — no se toca en este
  intent); (ii) medir el piso de cobertura sobre la suite estabilizada ANTES de
  fijar `--cov-fail-under`; (iii) confirmar que la deuda de lint/audit está
  saneada/silenciada quirúrgicamente antes de promover a bloqueante. Documentar
  estos checks como precondición de cada push.
- B. Sin checks previos documentados.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de Deployment Execution (config-only; el despliegue son
los commits `chore(ci)` a `main`, no codigo de app):

- **Q1 — Naturaleza (A)**: config del gate via commits `chore(ci)`; el
  deployment-log documenta procedimiento y estado esperado, sin fabricar un push
  no ejecutado.
- **Q2 — Migraciones (A)**: ninguna; no toca esquema ni datos de Neon.
- **Q3 — Smoke/health (A)**: comportamiento esperado de los checks existentes
  (`/health` 5 reintentos HTTP 200; `/health` y `/`); identico a la linea base
  (verde); verificacion real al pushear cada commit. Sin inventar resultados.
- **Q4 — Ventana/secuencia (A)**: 8 commits `chore(ci)` escalonados, cada uno
  verde en ambos gates antes del siguiente; rollback quirurgico por commit; sin
  freeze especial (deploy on-merge, single-maintainer).
- **Q5 — Pre-deployment checks (A)**: reproducir el gate en local; medir el piso
  antes de fijarlo; deuda de lint/audit saneada/silenciada antes de bloquear.

Se generaran: `deployment-log.md`, `smoke-test-results.md` y
`health-check-report.md`, respetando el mandato coste 0 EUR, la cadena `needs:`
intacta y todas las reglas afirmadas.

[Answer]: Looks correct
