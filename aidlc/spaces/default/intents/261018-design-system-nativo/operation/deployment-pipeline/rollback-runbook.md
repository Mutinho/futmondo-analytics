# Rollback Runbook — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Qué puede necesitar rollback

Este intent cambia código iOS (librería del sistema de diseño + login revestido), **no** producción de servidor. El "rollback" es a nivel de código fuente y de app instalada.

## Procedimiento de reverso

1. **Código (git)**: el intent aterriza como un squash-commit en `main`. Para revertir: `git revert <sha>` del commit del intent (no destructivo), que restaura el login de F1 ad-hoc y retira la librería `DesignSystem`. El gate de CI valida el revert como cualquier PR.
2. **App en dispositivo**: reinstalar la build anterior con `cd ios && xtool dev build` desde el commit revertido (firma gratuita).
3. **Backend/frontend producción**: no aplica — este intent no los toca; su rollback (runbook `docs/ROLLBACK.md`, redeploy de release anterior en Fly.io) permanece intacto y no se invoca por este intent.

## Verificación tras rollback

- `cd ios && swift build && swift test` verde.
- Login funcional en el iPhone 13 Pro (comportamiento de F1).

## Assumptions & Open Questions

None.
