# Preguntas — Environment Provisioning (Fiabilidad de la sync)

> Conversation language: Spanish. Fase Operation. **Adaptación de stack** (regla
> afirmada en `project.md`): el conocimiento del stage asume AWS/CloudWatch,
> pero el stack real es **Fly.io + Neon PostgreSQL** a coste 0 €. El entorno
> **ya está provisionado y en producción**; esta etapa documenta su inventario
> y valida que soporta el intent (backend-only, aditivo). Lo que exige servicios
> de pago se marca NO-APLICA/diferido. Respuestas determinadas por el entorno
> real (Operation: preguntas excepcionales).

## Q1 — ¿Están todos los entornos provisionados?

A. Sí — producción única ya provisionada (Fly.io `cdg` + Neon Frankfurt), sin staging separado
B. No / parcialmente
X. Other (please specify)

[Answer]: A. Sí. Producción única en Fly.io: backend `futmondo-api` (8000, check `/health`) y frontend `futmondo-app` (nginx, 80, check `/`); BD Neon PostgreSQL (Frankfurt, free). No hay staging (restricción coste 0 €). NO-APLICA: VPC/subnets/NACLs (concepto AWS; Fly.io gestiona la red).

## Q2 — ¿Configuración de red correcta (VPC, subnets, security groups, NACLs)?

A. NO-APLICA en AWS terms; Fly.io gestiona red/routing; el acceso a Neon es por connection string TLS
B. Requiere revisión
X. Other (please specify)

[Answer]: A. NO-APLICA en términos AWS. Fly.io expone las apps por HTTPS y enruta internamente; la conexión a Neon usa `DATABASE_URL` (TLS). No hay VPC/SG/NACL que provisionar. Este intent no cambia topología de red.

## Q3 — ¿Secretos correctamente inyectados?

A. Sí — vía `secrets` de Fly.io / GitHub Actions (`DATABASE_URL`, `JWT_SECRET`, `FLY_API_TOKEN`); nunca literales
B. Requiere revisión
X. Other (please specify)

[Answer]: A. Sí. `DATABASE_URL` y `JWT_SECRET` como Fly secrets del backend; `FLY_API_TOKEN` como secret de GitHub Actions. `JWT_SECRET` no-default exigido en arranque (NFR1.1). El intent no añade secretos nuevos. NO-APLICA: AWS Secrets Manager/Parameter Store.

## Q4 — ¿Conectividad cross-account / cross-VPC validada?

A. NO-APLICA (sin múltiples cuentas/VPC); la única conectividad externa es backend→Neon (TLS) y frontend→backend (proxy nginx)
B. Requiere validación
X. Other (please specify)

[Answer]: A. NO-APLICA. Arquitectura de un entorno: frontend (nginx) proxya a `futmondo-api`, que conecta a Neon por TLS. Sin cross-account/cross-VPC. El intent no cambia rutas de conectividad.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
