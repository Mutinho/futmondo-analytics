# Deployment Pipeline — Preguntas (Intent 4: gate CI/CD hardening)

> Etapa de fase Operation. La topología y el orden de despliegue **no cambian**
> en este intent config-only: la cadena `needs:` (`verify → deploy-backend →
> deploy-frontend → smoke-test`) se mantiene; el intent endurece el CONTENIDO
> del job `verify` (pre-deploy gate), no el CD. Lo ya afirmado (deploy on-merge,
> sin staging, smoke test `/health`, rollback manual `fly releases rollback`,
> secretos vía `secrets`, coste 0 €) NO se re-pregunta. Estas preguntas cierran
> el encuadre de los artefactos de CD.

---

## Q1 — Encuadre del artefacto `cd-config.md`

El CD ya existe y no cambia su topología. ¿Qué documenta `cd-config.md`?

- A. **CD existente + el impacto del endurecimiento del gate pre-deploy como
  delta**: documentar la cadena `needs:` intacta, los jobs de deploy
  (`deploy-backend`/`deploy-frontend` con `flyctl deploy`), el smoke test, y
  explicitar que lo único que cambia es el CONTENIDO del job `verify` (gate
  endurecido, ya especificado en `ci-config.md`), marcando qué NO cambia.
- B. **Redocumentar el CD completo desde cero** con todo el detalle.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Condiciones de aborto del deploy tras endurecer `verify`

El job `verify` gana pasos bloqueantes (audits, lint, piso de cobertura). ¿Cómo
se documenta el efecto en las condiciones de aborto del deploy?

- A. **El gate endurecido amplía las condiciones de aborto pre-deploy sin
  cambiar el mecanismo**: si CUALQUIER paso de `verify` (incluidos los nuevos:
  pip-audit, npm audit, ruff check, piso de cobertura, expiry) falla, los jobs
  `deploy-*` (que dependen de `verify` vía `needs:`) no se ejecutan — un rojo
  nunca llega a producción. El mecanismo (`needs:`) es el mismo; solo hay más
  razones por las que `verify` puede fallar.
- B. Introducir condiciones de aborto/rollback nuevas más allá de las de
  `verify` + smoke test.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Rollback runbook: reutilizar o reescribir

Ya existe `docs/ROLLBACK.md` (rollback manual Fly.io, `fly releases rollback`,
verificación `/health`). ¿Qué hace `rollback-runbook.md` de esta etapa?

- A. **Reutilizar y referenciar `docs/ROLLBACK.md`** como fuente única del
  procedimiento (sin cambios en el mecanismo de rollback), y añadir solo el
  matiz de este intent: cada endurecimiento del gate va en commit `chore(ci)`
  aislado, de modo que un rollback quirúrgico de un cambio de gate es revertir
  ese commit (distinto del rollback de release de Fly.io, que sigue igual).
- B. **Reescribir el runbook completo** en el artefacto de la etapa.
- X. Other (please specify)

[Answer]: A

---

## Q4 — `deployment-strategy.md` y las guardrails de fase Operation

Las guardrails de Operation piden documentar criterios de traffic-shifting/abort
para blue-green/canary y SLOs cuantificados. ¿Cómo se resuelve en este stack?

- A. **Documentar la estrategia real (redeploy on-merge, sin blue-green/canary)
  y marcar NO-APLICA lo de pago**: el stack es dos apps Fly.io con redeploy
  directo; no hay traffic-shifting gradual (blue-green/canary exigirían
  infraestructura/coste). El criterio de éxito/abort es el smoke test `/health`
  (5 reintentos, HTTP 200). SLO formal con burn-rate = NO-APLICA (de pago); SLI
  informal = `/health` 200. Documentar la alternativa gratuita, sin inventar
  infraestructura inexistente.
- B. Diseñar una estrategia blue-green/canary nueva para este intent.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Gates de promoción de entorno (dev → staging → prod)

El proyecto no tiene staging separado (deploy on-merge a producción). ¿Cómo se
documentan los "environment promotion gates"?

- A. **Un único entorno de producción, sin promoción multi-entorno**: el "gate
  de promoción" a producción es el gate de CI bloqueante (PR + `verify`) + el
  smoke test post-deploy. Documentar que no hay dev/staging separados (línea
  base afirmada) y que la promoción es implícita (merge a `main` → deploy).
- B. Introducir un entorno de staging nuevo.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de la etapa de Deployment Pipeline (config-only; CD sin
cambios de topologia):

- **Q1 — `cd-config.md` (A)**: CD existente + delta del gate pre-deploy
  endurecido; cadena `needs:` y jobs de deploy intactos; solo cambia el contenido
  de `verify`. Marcar que NO cambia.
- **Q2 — Condiciones de aborto (A)**: el gate endurecido amplia las razones por
  las que `verify` puede fallar (pip-audit, npm audit, ruff, piso, expiry); mismo
  mecanismo `needs:`; un rojo nunca llega a produccion.
- **Q3 — Rollback (A)**: reutilizar/referenciar `docs/ROLLBACK.md` (mecanismo sin
  cambios) + matiz del rollback quirurgico por commit `chore(ci)`.
- **Q4 — `deployment-strategy.md` (A)**: estrategia real (redeploy on-merge, sin
  blue-green/canary); smoke test `/health` como criterio de exito/abort; SLO con
  burn-rate NO-APLICA (de pago), SLI informal `/health` 200.
- **Q5 — Gates de promocion (A)**: un unico entorno de produccion; promocion
  implicita (merge a `main` -> deploy); sin staging separado.

Se generaran: `cd-config.md`, `deployment-strategy.md` y `rollback-runbook.md`,
respetando el mandato coste 0 EUR, la cadena `needs:` intacta y todas las reglas
afirmadas.

[Answer]: Looks correct
