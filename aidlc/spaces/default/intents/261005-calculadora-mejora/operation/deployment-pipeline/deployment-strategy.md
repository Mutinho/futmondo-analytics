# Deployment Strategy — calculadora-mejora

## Estrategia: on-merge continuo a producción (Fly.io)

- **Modelo**: trunk-based; cada merge a `main` que pasa el gate se despliega a
  producción Fly.io. Sin entorno de staging separado.
- **Verificación de release**: smoke test `/health` (5 reintentos, HTTP 200) tras
  `deploy-backend` y `deploy-frontend`.
- **Blue/green, canary, A/B**: **NO-APLICAN** en este stack/tier. Justificación:
  Fly.io free allowance + topología de dos apps no sostiene entornos duplicados
  sin coste; el cambio es un toggle de UI de bajo riesgo. Alternativa de
  seguridad real = el gate bloqueante + smoke test + rollback por redeploy.
- **Trade-off aceptado**: versiones mixtas momentáneas durante el rollout de
  nginx son irrelevantes para un cambio puramente de cliente (el toggle y su
  `localStorage` son por navegador).

## Migraciones de BD

- **Ninguna**. El cambio no toca esquema ni datos (frontend-only). No se aplica
  expand-contract.

## Ventanas / freeze

- Sin ventanas formales ni freeze (proyecto single-maintainer); el gate
  bloqueante es la protección.

## Checklist de despliegue (aplicable)

- [x] Gate de CI bloqueante en verde antes de merge (gitleaks + pytest + ng test).
- [x] Smoke test `/health` configurado en la cadena de deploy.
- [x] Rollback documentado (ver `rollback-runbook.md`).
- [x] Sin cambios de esquema / backward-compat trivial (frontend-only).
- [N/A] Blue/green, canary, connection draining avanzado (no aplican al tier).

## Sources

- `team.md` → `## Deployment`; `cd-config.md`; `knowledge/aidlc-shared/operation-fly-stack.md`.
- `knowledge/aidlc-pipeline-deploy-agent/deployment-strategies.md` (adaptado a Fly.io).

## Assumptions & Open Questions

None.
