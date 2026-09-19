# Especificación de Infraestructura — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). **No introduce infraestructura desplegable nueva.** El intent es una intervención sobre configuración de tests y workflows de CI; no crea servicios, bases de datos, colas ni recursos cloud.

## Infraestructura afectada (existente, sin cambios de topología)

| Recurso | Rol | Cambio por este intent |
|---------|-----|------------------------|
| GitHub Actions (free tier) | Ejecuta el gate de CI (`ci.yml`, `fly-deploy.yml`) | Se corrige el comando `ng test` para ejercitar cobertura; runners `node-version: '22'`. Sin runners ni servicios nuevos. |
| Fly.io (región `cdg`, free allowance) | Aloja backend `futmondo-api` y frontend `futmondo-app` (nginx) | **Sin cambios**: misma topología, mismo orden de despliegue, mismo healthcheck `/health`. |
| Neon PostgreSQL (Frankfurt, free) | Base de datos | **Sin cambios**: no la toca el intent. |
| npm registry | Fuente del proveedor de cobertura `@vitest/coverage-v8` (OSS) | Nueva devDependency a versión exacta; sin servicio de pago. |

## IaC

- **No aplica**: no hay CDK, CloudFormation, Terraform ni recursos cloud que provisionar. El despliegue sigue siendo `flyctl deploy` orquestado por `fly-deploy.yml` (existente). No se escribe IaC nueva.
- **AWS/CloudWatch**: **NO-APLICA** — el stack real es Fly.io + GitHub Actions, no AWS. Cualquier patrón del conocimiento del agente que asuma AWS se adapta o se marca fuera de aplicación (aprendizaje afirmado en `project.md`).

## Restricción de coste

- Coste 0 €: todo en tiers gratuitos (GitHub Actions free, Fly.io free allowance, Neon free); proveedor de cobertura OSS. No se añade ningún recurso con gasto recurrente.

## Assumptions & Open Questions

- None.
