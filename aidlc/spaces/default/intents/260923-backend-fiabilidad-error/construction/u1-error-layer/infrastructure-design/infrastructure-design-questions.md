# Infrastructure Design — U1 `u1-error-layer` (preguntas)

Unidad: **U1 capa de errores** (`kind: library`). Sin infraestructura nueva.
Artefactos aplicables por kind: `cicd-pipeline`, `traceability`.

## Sources

- [desc] Initial description: "Mantener stack actual (FastAPI/Neon/Fly.io), sin cambios de infraestructura; gate CI bloqueante (gitleaks + pytest + ng test). FR3.2.3 re-habilita E722 advisory. Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/team.md#Deployment`: "ESTE intent no cambia la topología ni el orden de despliegue."

---

## Q1. Incidencia de U1 en infraestructura / pipeline

- A. **Ninguna infraestructura nueva; solo el gate CI existente**: U1 es una biblioteca de tipos que vive dentro de `futmondo-api` (Fly.io ya definido). No hay recursos cloud nuevos, ni cambios de topología. La única incidencia en el pipeline es (a) el commit aislado `chore(ci)` que quita `E722` del `ignore` de `backend/ruff.toml` (FR3.2.3, ruff sigue advisory), y (b) que la suite de U1 corre en el gate CI existente (`ci.yml` + job `verify`). Coste 0 €.
- B. Otra cosa (indícala en Other).
- X. Other (please specify)

[Answer]: A. Ninguna infraestructura nueva; solo el gate CI existente. Única incidencia: (a) commit aislado chore(ci) que quita E722 del ignore de backend/ruff.toml (ruff sigue advisory), (b) la suite de U1 corre en ci.yml + job verify. Coste 0 €.

## Consolidated Summary Confirmation

Resumen de infra de U1 (antes de fijar los artefactos):

- **Sin infraestructura nueva (Q1=A)**: U1 vive dentro de futmondo-api (Fly.io ya definido). Sin recursos cloud, sin cambio de topología.
- **Pipeline**: commit aislado chore(ci) para E722 advisory (FR3.2.3); la suite de U1 corre en el gate CI existente. Coste 0 €.
- **Artefactos** (kind=library): cicd-pipeline.md, traceability.json.

[Answer]: Looks correct
