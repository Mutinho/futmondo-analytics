# Preguntas — Code Generation (Optimización del bundle inicial)

> Stage 3.5 Code Generation · Intent `260914-bundle-optimization` · scope refactor · Minimal.

## Plan Approval

¿Apruebas este plan exacto de generación de código?

Cubre `code-generation-plan.md` (con su Testing Contract embebido) y `unit-test-instructions.md`. El plan aplica un refactor de configuración de carga en `angular-app/`: sacar Chart.js/ng2-charts y `marked` del chunk inicial, cambiar `PreloadAllModules` por una estrategia de precarga con retardo propia (coste 0 €), y — solo después — restaurar el budget `initial` a `maximumError: 1MB`. Sin cambio funcional.

[Approval Fingerprint]: sha256:v3:b6015d9047ea1bc1e445b1873c773a09bb3c3a05def70b2e95e916f1a08135e1
[Planned Source]: baf2d507dbead7f9256630234e334980dbc964afd37f40f8135884cb9892cbc6

- Approve Plan
- Request Changes

[Answer]: Approve Plan
