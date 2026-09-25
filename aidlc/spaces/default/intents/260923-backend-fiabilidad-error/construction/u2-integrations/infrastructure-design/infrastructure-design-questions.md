# Infrastructure Design — Preguntas · u2-integrations (Integraciones)

Fase Construction, profundidad Standard. Este intent **no cambia la
infraestructura**: la memoria de Deployment y `logical-components.md` ya fijan
que la topología (dos apps Fly.io, Neon, crons one-shot, orden de despliegue,
rollback) queda sin cambio, y los patrones de U2 viven en el código, no en la
infra. Adaptado a coste 0 € (sin recursos AWS). Sólo queda **una** decisión de
diseño de pipeline por confirmar.

Perspectiva inline: plataforma (Fly.io, lead) + DevSecOps + Compliance.

---

## Q1 — Encaje del cambio de config `E722` (advisory) en el pipeline

FR3.2.3 re-habilita `E722` (bare-except) como **advisory por trinquete** en
`backend/ruff.toml` (quitándolo del `ignore`), sin promover `ruff check` a
bloqueante, en un **commit aislado** (`chore(ci)`), sin `--fix` ni `ruff
format`. ¿Cómo lo reflejamos en el diseño de infraestructura/pipeline de U2?

- A. Documentarlo en `cicd-pipeline.md` como un **cambio de config aislado**
  dentro del pipeline existente (`ci.yml` + job `verify` de `fly-deploy.yml`),
  SIN cambiar la cadena `needs:` ni promover ruff a bloqueante; `ruff check`
  sigue advisory y sólo reporta. El resto de la infra/pipeline queda sin cambio.
- B. Aprovechar para promover `ruff check` a bloqueante en el pipeline.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
