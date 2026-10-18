<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
2026-10-18 — El entorno (Fly.io + Neon) ya existe y está operativo: environment-provisioning documenta y valida el entorno real en vez de provisionar nada nuevo. D-01 ya desplegado; la app iOS no es un entorno gestionado (firma gratuita en un dispositivo).

## Deviations
2026-10-18 — infrastructure-specification.md no existe (infrastructure-design `skipped` en los 3 bolts): se documenta la ausencia y se toma el entorno real, sin inventar infra.
2026-10-18 — No se invoca devsecops/compliance (collaborators off, sin infra nueva que auditar); los controles de seguridad de F1 ya están verificados en etapas previas.

## Tradeoffs
2026-10-18 — Términos AWS del stage (VPC/subnets/Secrets Manager/cross-VPC) marcados NO-APLICA; validación con herramientas gratuitas (curl /health en vivo, fly logs/status). Coste 0 €.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
