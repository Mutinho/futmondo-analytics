# Deployment Strategy — F1: Login nativo end-to-end

> Fase: operación (deployment-pipeline). Idioma: castellano; tokens técnicos verbatim en inglés.
> Documenta la estrategia de despliegue de los dos entregables de F1 contra el stack real
> (Fly.io + Neon, coste 0 €) sin inventar infraestructura.

## Principios aplicados

- **Rollback no es opcional**: cada canal tiene su ruta de reversión (ver `rollback-runbook.md`).
- **El despliegue no está hecho hasta que el smoke pasa**: el backend verifica `/health`; la app
  iOS se valida manualmente en el dispositivo (login → auto-login → logout).
- **Un rojo nunca llega a producción**: el gate `verify` bloquea el deploy del backend.
- **Coste 0 €** salvo la excepción acotada (publicación nativa, diferida).

## Canal 1 — Backend D-01 (Fly.io)

- **Estrategia**: **recreate on-merge** (sustitución de la release de Fly.io al hacer `flyctl
  deploy`). No hay blue/green ni canary: el stack es de entorno único y tier gratuito; Fly.io hace
  rolling de máquinas pero no se orquesta canary con métricas (sería de pago / NO-APLICA).
- **Disparo**: merge/push a `main` → `fly-deploy.yml`.
- **Gate de promoción**: job `verify` (bloqueante) antes de `deploy-backend`. No hay promoción
  multi-entorno (sin staging); la promoción efectiva es verde-en-`verify` → producción.
- **Verificación post-deploy (smoke)**: `smoke-test` hace `curl` a `https://futmondo-api.fly.dev/health`
  (5 reintentos, HTTP 200). Si falla, el workflow queda en rojo y se activa el rollback manual.
- **Retrocompatibilidad (clave de D-01)**: el cambio es **aditivo**. La resolución del refresh token
  sigue la precedencia cookie → header `X-Refresh-Token` → body; el login ahora devuelve también
  `refresh_token` en el body. La PWA existente (cookie `HttpOnly`) no se ve afectada porque la
  cookie gana la precedencia y la PWA ignora el `refresh_token` del body. Por eso **no se necesita
  feature flag** ni ventana de migración: cliente viejo y cliente nativo nuevo conviven sobre la
  misma release.
- **Migraciones de BD**: **ninguna**. D-01 no toca el esquema de Neon.

## Canal 2 — App iOS (`xtool`, firma gratuita)

- **Estrategia**: instalación directa sobre el dispositivo del propietario (**recreate** por
  reinstalación). No hay distribución a múltiples dispositivos ni fases de rollout: un único
  dispositivo objetivo (iPhone 13 Pro).
- **Disparo**: manual — el propietario ejecuta `ios/scripts/install-app.sh` cuando quiere
  (re)instalar.
- **Gate de promoción**: la lógica se verifica con `swift test` (29 passed) antes de instalar; la
  validación funcional es manual en el dispositivo.
- **Verificación post-deploy (smoke manual)**: flujo F1 en el iPhone — login contra el backend
  prod → cerrar y reabrir la app (auto-login recuperando el refresh token del Keychain) → logout.
- **Caducidad de firma**: ~7 días (free-signing). El "redespliegue" periódico es re-ejecutar el
  script. **Publicación en App Store diferida (B-09)**: requiere Apple Developer Program (~99 €/año),
  excepción acotada de coste, fuera de alcance de F1.

## Estrategias NO aplicadas y por qué

| Estrategia | Decisión | Rationale |
|------------|----------|-----------|
| Blue/Green | NO-APLICA | Entorno único Fly.io tier gratuito; sin recursos para duplicar entorno. |
| Canary con métricas | NO-APLICA | Requiere observabilidad gestionada de pago; coste 0 €. |
| Feature flags | NO-APLICA | D-01 es retrocompatible por precedencia; no hay cambio que esconder. |
| Promoción multi-entorno (dev→staging→prod) | Sustituido | Sin staging; el smoke `/health` es la verificación de release. |
| Distribución OTA / TestFlight | Diferido (B-09) | Requiere Apple Developer Program de pago. |

## Sources

- [consumes] cd-config.md; ci-config.md, quality-gates.md (construction/ci-pipeline).
- [code] `.github/workflows/fly-deploy.yml`, `ios/scripts/install-app.sh`.
- [memory] team.md `## Deployment` (on-merge, sin staging, smoke `/health`); project.md (coste 0 €
  + excepción acotada); aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
