<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-16T13:38Z — Ruta técnica elegida: Swift/SwiftUI nativo puro + `xtool` como ruta ÚNICA (QF1=C). Angular existente degradado a especificación funcional de referencia, no código a migrar. Reutilizable: backend FastAPI (HTTP, intacto) + conocimiento de dominio.
- 2026-10-16T13:38Z — Documentación oficial de `xtool` (xtool.sh/documentation/xtool) consultada y verificada: cross-platform Linux/WSL/macOS; build SwiftPM→app iOS; firma+instala apps iOS; en Windows vía WSL (Swift 6.4 toolchain + usbmuxd + USB passthrough). Con cuentas gratuitas prefija el bundleID (XTL-xxxx.) y wildcard provisioning sólo con cuenta de pago. Config vía `xtool.yml` (version/bundleID/product/extensions); widgets vía App Extensions soportados. Usuario ya tiene WSL operativo (QF3b=A).
- 2026-10-16T13:38Z — Auth (QF4=B): cliente Swift guarda refresh token en iOS Keychain; el flujo cookie HttpOnly puede obligar a ajuste mínimo en `/auth/refresh` (aceptar token por header/body), a documentar como dependencia sin tocar backend. Firma gratuita al máximo con Apple ID gratuito (QF3=A), caducidad ~7 días asumida. Sin plazo (QF5=A).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-16T13:38Z — Reencuadre respecto a intent-capture: el intent-statement decía "partiendo del código Angular existente". Con Swift nativo puro NO se porta la UI/lógica Angular; se reescribe. El Angular queda como especificación de referencia. Desviación aprobada explícitamente por el usuario ("Si, a por Swift").
- 2026-10-16T13:38Z — Consulté documentación web externa (xtool.sh) durante una etapa de análisis. Normalmente las estimaciones de viabilidad se marcan como supuesto; aquí el usuario pidió explícitamente consultar la web, así que los datos de `xtool` se registran como fuente verificada, no como supuesto.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-16T13:40Z — Validar en un spike la cadena `xtool` end-to-end (build Swift → firma gratuita → instalación en iPhone 13 Pro desde WSL) y el ciclo de refirmado a ~7 días (R-01/R-02).
- 2026-10-16T13:40Z — Verificar leyendo el backend si `/auth/refresh` depende de cookie HttpOnly y requiere aceptar el refresh token por header/body para clientes nativos (D-01, intent posterior).
