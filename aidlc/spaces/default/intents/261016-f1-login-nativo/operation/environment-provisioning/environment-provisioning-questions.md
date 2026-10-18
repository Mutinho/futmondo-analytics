# Environment Provisioning — Preguntas y confirmación — F1: Login nativo end-to-end

> Fase: operación (environment-provisioning). Idioma: castellano; tokens técnicos verbatim en
> inglés.

## Preguntas de clarificación

Las preguntas del stage (entornos provisionados per Infra Design, VPC/subnets/security groups,
secretos inyectados, conectividad cross-account) se resuelven contra el entorno **ya existente**;
no hay provisión nueva ni preguntas abiertas:

- **¿Entornos provisionados?** Sí, preexistentes: Fly.io (`futmondo-api` + `futmondo-app`, región
  `cdg`) + Neon (Frankfurt). F1 no provisiona infra nueva.
- **¿VPC/subnets/security groups/NACL correctos?** NO-APLICA: Fly.io gestiona red/routing.
- **¿Secretos correctamente inyectados?** Sí: `FLY_API_TOKEN`, `JWT_SECRET` (no-default),
  `DATABASE_URL` vía Fly.io/GitHub Actions secrets. D-01 no añade ni rota secretos.
- **¿Conectividad validada?** Sí: app iOS → backend prod (TLS) verificada por el flujo de login
  real; backend → Neon confirmado por `/health` 200.

## Consolidated Summary Confirmation

Resumen de lo producido en environment-provisioning para F1:

- **Sin provisión nueva**: el entorno de producción (Fly.io `futmondo-api` + `futmondo-app`, región
  `cdg`; Neon Frankfurt) ya existe y está operativo. F1 no cambia la topología; D-01 redesplegó el
  backend de forma aditiva y la app iOS se instala por firma gratuita con `xtool` (no es un entorno
  gestionado).
- **environment-inventory.md**: inventario del entorno real, auditoría de secretos (sin regresión;
  D-01 no añade secretos), conectividad TLS y mapeo AWS → equivalente gratuito.
- **validation-report.md**: entorno validado con herramientas gratuitas — `/health` verificado en
  vivo (HTTP 200 `{"status":"healthy"}` el 2026-10-18); D-01 desplegado y verde; refresh token en
  iOS Keychain; flujo iOS login → auto-login → logout validado en el iPhone 13 Pro.
- **Adaptación al stack**: VPC/subnets/Secrets Manager/cross-VPC marcados NO-APLICA; auditoría de
  secretos sustituida por Fly.io/GitHub Actions secrets; sin invocar devsecops/compliance (no hay
  infra nueva que auditar, `collaborators: off`). No se inventa infraestructura:
  `infrastructure-specification` no existe (infrastructure-design `skipped` en los 3 bolts).

¿Es todo correcto?

[Answer]: Looks correct
