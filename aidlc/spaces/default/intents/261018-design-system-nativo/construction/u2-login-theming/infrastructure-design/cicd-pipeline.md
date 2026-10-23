# CI/CD Pipeline — U2 `u2-login-theming`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

## Verificación de la Unit

- **Check / checkpoint**: `cd ios && swift build && swift test` (comando autorizado del intent). Al revestir `LoginView` (en `FutmondoApp`, guardado `#if canImport(SwiftUI)`), lo esencial es que `swift build` siga compilando y que `swift test` (cobertura de `FutmondoKit`) siga en verde sin regresión.
- **Verificación en dispositivo** (manual): login revestido en el iPhone 13 Pro — login → auto-login → logout sin regresión, aspecto coherente con el sistema de diseño, claro/oscuro y Dynamic Type (`xtool` desde WSL, firma gratuita).

## CI/CD del repositorio

Estado heredado no modificado por U2 (igual que U1). Job Swift en GitHub Actions diferido (D-CI de F1). Sin AWS.

## NO-APLICA

| Aspecto estándar (AWS) | Estado |
|------------------------|--------|
| infrastructure-specification | NO-APLICA (revestimiento de UI) |
| monitoring-design | NO-APLICA (sin servicio desplegado) |
| CDK / recursos AWS | NO-APLICA |

## Assumptions & Open Questions

None.
