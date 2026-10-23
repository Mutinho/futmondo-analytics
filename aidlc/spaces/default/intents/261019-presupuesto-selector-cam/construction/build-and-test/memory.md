<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20T09:58Z — Build and Test (integración U1+U2): `swift build && swift test` = Build complete + **87 tests, 0 fallos** (43 F1 + 39 U1 + 5 U2). Seguridad (no-fuga, HTTPS, UserDefaults sólo id) verificada por tests de U1 y preservada en U2. UI/experiencia (60fps, <100ms, VoiceOver, Dynamic Type, fidelidad, flujo end-to-end + logout) pendiente de validación en iPhone 13 Pro (se registra en Performance Validation de Operación). Cross-unit traceability cubre todos los FR Must. Nota: `ios/.build/*` (artefactos de compilación) cambió fuera de las unidades; es ruido de build, no fuente.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-20T12:37Z — Build and Test re-recorrido tras el re-trabajo de U2 (reopen desde ci-pipeline): estado final `swift build && swift test` = **105 tests, 0 fallos** (F1+U1+U2 incl. FR6 detalle). Compila para arm64 en dispositivo; validado por el propietario en iPhone 13 Pro (tema oscuro, cards neón, tab bar flotante, detalle con zoom/animaciones). Seguridad/no-fuga/HTTPS preservados; sin deps nuevas; sesión F1 intacta. Deuda registrada: desajuste de "saldo" lista vs detalle = inconsistencia del backend (otro intent). Resto pendiente de dispositivo = ninguno nuevo (validado en vivo).