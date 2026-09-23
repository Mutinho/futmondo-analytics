# Preguntas — CI Pipeline (Fiabilidad de la sync)

> Conversation language: Spanish. Intent acotado y aditivo: la CI del proyecto
> **ya existe** y es adecuada (`.github/workflows/ci.yml` + job `verify` de
> `fly-deploy.yml`, con `pytest`/`ng test`/gitleaks bloqueantes). Esta etapa
> **documenta** la config y los quality gates y verifica que ejercen los
> comandos de Build and Test; no reescribe la pipeline. Las respuestas están
> determinadas por la CI real presente en el repo (Construction: preguntas
> excepcionales).

## Q1 — ¿Qué herramienta de CI se usa?

A. GitHub Actions
B. CodePipeline/CodeBuild
C. Jenkins
D. Otra
X. Other (please specify)

[Answer]: A. GitHub Actions (`.github/workflows/ci.yml` en PR→`main`; job `verify` de `fly-deploy.yml` en push→`main`).

## Q2 — ¿Estrategia de ramas?

A. Trunk-based (ramas cortas, MR a `main` con gate de CI obligatorio)
B. GitFlow
C. Otra
X. Other (please specify)

[Answer]: A. Trunk-based sobre `main`; squash-merge; gate de CI obligatorio (required status check) en el MR, replicado en `verify` para el push directo.

## Q3 — ¿Qué quality gates son obligatorios antes de fusionar?

A. Tests (pytest + ng test) + escaneo de secretos (gitleaks), BLOQUEANTES; lint/audits ADVISORY
B. Solo tests
C. Solo lint
X. Other (please specify)

[Answer]: A. Bloqueantes: `pytest` (backend), `ng test` con cobertura por métrica (frontend), gitleaks. Advisory: ruff/ESLint y pip-audit/npm audit. Sin cambios por este intent (backend-only): los tests nuevos de `sync-reliability` ya corren bajo `pytest tests`.

## Q4 — ¿Repositorios de artefactos?

A. Ninguno específico (deploy directo a Fly.io por imagen); GitHub Actions free
B. ECR/CodeArtifact/S3
X. Other (please specify)

[Answer]: A. No hay repos de artefactos dedicados; el deploy lo hace `fly-deploy.yml` a Fly.io (región `cdg`). Todo en tiers gratuitos (coste 0 €).

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
