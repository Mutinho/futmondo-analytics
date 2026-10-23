# CI/CD Pipeline — U1 `u1-design-system`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.
> U1 es una librería SwiftUI (kind `library`) embebida en `ios/`. Sin infraestructura ni despliegue propio. Adaptado al stack real (no AWS).

## Verificación de la Unit

- **Check local/checkpoint**: `cd ios && swift build && swift test` — aprobado como comando de verificación de checkpoint en delivery-planning y pineado en `nfr-requirements/tech-stack-decisions.md`. Compila el módulo `DesignSystem` dentro del paquete SwiftPM y corre los tests unitarios que existan. Reproducible a coste 0 €.
- **Instalación en dispositivo** (manual, fuera del checkpoint automatizado): `xtool` desde WSL con firma gratuita, como en F1, para verificación visual (claro/oscuro, Dynamic Type) en el iPhone 13 Pro.

## CI/CD del repositorio

- El gate de CI del repo (`.github/workflows/ci.yml` job `quality`, y `fly-deploy.yml` job `verify`) es **estado heredado** y gobierna backend (`ruff`/`pytest`/`pip-audit`) y frontend Angular (`ng test`/`npm audit`). **Este intent NO lo modifica**: una librería iOS que se compila con `xtool`/`swift` no entra hoy en esos workflows.
- **Deuda registrada (ya anotada en F1)**: un job de Swift (`swift test`) en GitHub Actions para la app iOS queda **diferido** (D-CI de F1), fuera del alcance de este intent de capa de diseño.

## NO-APLICA (adaptación al stack real)

| Aspecto estándar (AWS) | Estado |
|------------------------|--------|
| infrastructure-specification | NO-APLICA (kind library; sin recursos cloud) |
| monitoring-design | NO-APLICA (kind library; sin servicio desplegado) |
| CDK / recursos AWS | NO-APLICA; stack Fly.io + Neon + app nativa iOS, sin AWS |

## Assumptions & Open Questions

None.
