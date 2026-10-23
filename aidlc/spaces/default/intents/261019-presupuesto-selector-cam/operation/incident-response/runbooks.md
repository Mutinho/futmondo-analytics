# Runbooks — F2 (Incident Response)

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

Sin incidentes de servidor nuevos (F2 es app cliente). Runbooks de los modos de fallo reales de la capa nativa:

## R1 — Regresión visual/funcional en Presupuesto o detalle
- **Síntoma**: tras una build, la pantalla de Presupuesto/detalle se ve mal o falla en el dispositivo.
- **Acción**: `git revert` del commit/PR de F2 y reinstalar la build previa (`./scripts/install-app.sh`); la sesión de F1 no se ve afectada. Reproducir con `swift build && swift test` en WSL para la parte de lógica; el render se valida en dispositivo.

## R2 — Caducidad de la firma gratuita (~7 días)
- **Síntoma**: la app deja de abrir en el iPhone (firma de desarrollo caducada).
- **Acción**: reejecutar `./scripts/install-app.sh` para refirmar+reinstalar. Si falla el provisioning (`Connection reset by peer` contra `api.appstoreconnect.apple.com`), comprobar `date` en WSL y el relay 27015, y reintentar.

## R3 — Error de datos en la pantalla (lista/detalle)
- **Síntoma**: la app muestra estado de error al cargar balances/campeonatos/detalle.
- **Acción**: es un fallo de red/backend; la app ya muestra "Reintentar" sin corromper el campeonato activo. Verificar salud del backend (`/health`) por sus medios existentes. Si el dato es incoherente (p. ej. saldo lista vs detalle), ver la **deuda de backend registrada** (inconsistencia de `balance` con/sin premios), no es fallo de la app nativa.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/operation/deployment-pipeline/rollback-runbook.md`
- `ios/scripts/install-app.sh`

## Assumptions & Open Questions

None.
