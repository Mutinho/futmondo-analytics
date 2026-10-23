# CI Config — Sistema de diseño nativo iOS

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

## Estado del CI del repositorio (heredado, no modificado)

El gate de CI bloqueante del repo ya existe y es estado heredado:
- `.github/workflows/ci.yml` (job `quality`, disparo `pull_request → main`): gitleaks + `ruff check` + `pytest` + `pip-audit` (backend) y `ng test` + `npm audit` (frontend Angular).
- `.github/workflows/fly-deploy.yml` (job `verify`): replica el gate en push a `main`.

**Este intent (sistema de diseño iOS) NO modifica `ci.yml` ni `fly-deploy.yml`.** El código iOS (`ios/`, SwiftPM) no entra hoy en esos workflows.

## iOS en CI — deuda diferida

Un job de GitHub Actions que corra `cd ios && swift build && swift test` para la app iOS queda **diferido** (deuda D-CI registrada desde F1). No se añade en este intent de capa de diseño: el gate de CI del repo gobierna backend/frontend Angular, y la verificación iOS es local (`swift test`) + dispositivo (`xtool`). Añadir el job Swift sería trabajo de un intent de CI/tooling, a coste 0 € (runner de GitHub Actions free, imagen con Swift).

## Verificación local del intent

`cd ios && swift build && swift test` (comando de checkpoint autorizado), reproducible a coste 0 €.

## Assumptions & Open Questions

- [assumption] El job Swift en CI se añadirá en un intent futuro (D-CI); este intent no lo incluye.
