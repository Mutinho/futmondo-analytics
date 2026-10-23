# Environment Inventory — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Adaptado al stack real (no AWS).

## Entornos relevantes para este intent

| Entorno | Qué es | Provisión | Coste |
|---------|--------|-----------|-------|
| Dev/build local | Toolchain de Swift 6.x en WSL/Linux | Ya instalado (F1); sin aprovisionamiento nuevo | 0 € |
| Dispositivo | iPhone 13 Pro con `xtool` + firma gratuita | Ya configurado (F1) | 0 € (firma gratuita) |

## Producción (heredado, no aprovisionado por este intent)

- Fly.io región `cdg`: `futmondo-api` (backend) + `futmondo-app` (frontend Angular); Neon PostgreSQL (Frankfurt). **No se toca**: la capa de diseño es cliente iOS y no despliega a estos entornos.

## NO-APLICA

| Estándar (AWS) | Estado |
|----------------|--------|
| Aprovisionar cuentas/recursos cloud (VPC, IAM, etc.) | NO-APLICA; sin AWS y sin recursos nuevos |
| IaC (CDK/Terraform) | NO-APLICA; nada que aprovisionar para una librería cliente |

## Assumptions & Open Questions

None.
