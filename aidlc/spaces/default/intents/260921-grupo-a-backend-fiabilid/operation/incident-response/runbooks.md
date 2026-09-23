# Runbooks — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: Fly.io + Neon,
> single-maintainer, coste 0 €. Runbooks MANUALES con herramientas gratuitas
> (`fly`, `curl`, `fly logs`). Automatización SSM/Lambda NO-APLICA.

## RB-1 — Release no sano tras deploy (`/health` ≠ 200)

**Detección**: job `smoke-test` de `fly-deploy.yml` en rojo, o `curl /health` ≠ 200.

**Pasos**:
1. Confirmar: `curl -sS https://futmondo-api.fly.dev/health`.
2. Ver causa: `fly logs --app futmondo-api` (últimos errores de arranque).
3. Si no hay fix inmediato → **rollback** (ver `rollback-runbook.md`):
   `fly releases rollback <vN> --app futmondo-api`.
4. Verificar `/health` 200 tras el rollback.
5. Abrir PR con el fix real (gate de CI verde antes de fusionar).

**Contacto/escalado**: single-maintainer (ver `escalation-matrix.md`).

## RB-2 — Paso de sync degradado (`prizes`/`phantoms`)

**Detección**: `fly logs --app futmondo-api | grep "sync step degraded"`
(emitido por `record_degraded_step`; campos `sync_step`, `reason`).

**Pasos**:
1. Identificar el paso y el motivo en el log (`sync_step=<paso>`, `reason=<motivo>`).
2. Evaluar impacto: es un paso **non-critical** — la Tarea global puede haber
   terminado igualmente (BR3/NFR1); el resto de la sync no se ve afectado.
3. Si el motivo es transitorio (p. ej. timeout de la API Futmondo) → relanzar la
   sync del campeonato afectado desde la UI.
4. Si es recurrente → abrir incidencia con el `reason` y el `task_id`.

**Nota**: este runbook es posible *gracias* al intent: antes, el fallo se
enterraba como `done` y no había señal.

## RB-3 — Rechazo de puja (422)

**Detección**: `fly logs` muestra 422 en `/api/v1/market/bid`.

**Pasos**:
1. Distinguir causa: `price <= 0` (positividad) o `price > PRICE_SANITY_CAP`
   (techo de sanidad, FR6). Ambos son rechazos **esperados** de validación de
   entrada, no fallos del servicio.
2. Si es una puja legítima bloqueada por el techo, revisar el valor de
   `PRICE_SANITY_CAP` (constante documentada en `market.py`); su ajuste sería un
   cambio de código con su propio PR, nunca un hotfix en caliente.

## RB-4 — BD Neon inaccesible (preexistente)

**Detección**: `/health` en rojo con error de conexión; `fly logs` con errores de pool.

**Pasos**:
1. Comprobar estado de Neon (panel Neon) y `DATABASE_URL`.
2. Los `except` del pool ahora **loguean contexto** (FR3.2) en vez de silenciar
   — usar ese log para diagnosticar.
3. Si Neon está caído, esperar restablecimiento (tier free) y verificar `/health`.

## NO-APLICA / diferido

- Runbooks automatizados SSM, auto-remediation Lambda, AWS Backup, DR
  multi-región: requieren servicios de pago; diferidos. Los procedimientos
  manuales de arriba cubren los modos de fallo del intent a coste 0 €.

## Sources

- `operation/observability-setup/{alarms,log-queries}.md`,
  `operation/deployment-pipeline/rollback-runbook.md`,
  `construction/sync-reliability/functional-design/functional-spec.md`.

## Assumptions & Open Questions

None.
