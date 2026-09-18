# Requisitos de Fiabilidad — Backend Security Hardening

> Scope `security-patch`, depth Minimal.

## Red de Seguridad de Tests (no regresión)

- **NFR-REL.1**: La suite existente (`pytest`, `ng test`) debe permanecer en verde tras las correcciones; es condición dura para fusionar (gate de CI bloqueante). Traza: NFR4, regla `## Mandated`. `[memory:project.md]`
- **NFR-REL.2** (FR9): La corrección del refresh token **mejora** la fiabilidad de la sesión: hoy un token activo con `expires_at` aware se rechaza por error (401 indebido), forzando re-login. Corregirlo restablece el refresco correcto de sesión. Traza: FR9. `[memory:architecture.md]`
- **NFR-REL.3**: Cada FR entrega al menos un test que congela el comportamiento correcto (o el corregido), cubriendo el camino de error donde aplique. Para FR9 se actualizan deliberadamente los tests de caracterización que hoy congelan el bug. Traza: NFR5. `[Q4]`

## Tolerancia a Fallos y Recuperación

- **NFR-REL.4**: Sin cambios en el mecanismo de despliegue ni de rollback (redeploy de release anterior en Fly.io, runbook `docs/ROLLBACK.md`). Las correcciones son deploy-on-merge como cualquier otra. `[memory:code-quality-assessment.md]`
- **NFR-REL.5** (FR6): Rechazar una puja inválida con 422 es un fallo controlado y explícito en el boundary; no deja estado inconsistente (no se ha llamado a Futmondo). Traza: FR6, guardrail de manejo de errores de Construcción. `[memory:phases/construction.md]`

## Assumptions & Open Questions

None.

<!-- Re-anclado 2026-09-17 (redo-jump; contenido sin cambios). -->

<!-- Re-guardado 2026-09-17 tras confirmación vigente (contenido sin cambios). -->
