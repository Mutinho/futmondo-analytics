# Rollback Runbook — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Rollback de la app nativa (desarrollo)

Como F2 no despliega a servidor, el "rollback" es a nivel de código/instalación local:

- **Revertir el código**: `git revert` del commit/PR de F2 en `main` y reinstalar la build anterior con `./scripts/install-app.sh` (vuelve a la app sin la pantalla de Presupuesto/detalle). La sesión de F1 (login) no se ve afectada por el revert de F2 porque su lógica no cambió.
- **Backend**: no aplica — F2 no toca backend; el runbook de rollback del servidor (`docs/ROLLBACK.md`, redeploy de la release anterior en Fly.io) sigue vigente para el backend, pero F2 no lo invoca.

## Verificación tras rollback

`cd ios && swift build && swift test` verde + arranque de la app en el iPhone 13 Pro (login → superficie previa).

## Sources

- `aidlc/spaces/default/memory/team.md` (Rollback: `docs/ROLLBACK.md`, redeploy Fly.io)
- `ios/scripts/install-app.sh`

## Assumptions & Open Questions

None.
