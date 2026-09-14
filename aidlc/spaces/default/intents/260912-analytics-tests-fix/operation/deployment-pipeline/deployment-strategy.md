# Estrategia de Despliegue — Arreglo de tests de AnalyticsService

## Estrategia
- **Deploy on merge** (org.md): merge a `main` dispara `fly-deploy.yml`.
- Tipo: despliegue directo (recreate) de las apps Fly.io tras pasar `verify`.
  No hay blue/green ni canary configurado (proyecto de coste 0€, una máquina).
- Promoción de entornos: single-trunk; no hay staging separado. El gate real es
  `verify` (pytest + ng test) antes de desplegar.

## Aplicabilidad a este cambio
- Cambio de bajo riesgo: solo un fichero de test. No altera el runtime de la app
  ni el contrato de `/api/v1/analytics/*`.
- Criterio de éxito del despliegue: `verify` en verde + smoke `/health` OK
  post-deploy.

## Gates
- `verify` BLOQUEANTE (pytest + ng test). Con este arreglo, verde.
- Smoke `/health` como verificación post-deploy (health check).

## Feature flags / migraciones
- No aplican a este intent.
