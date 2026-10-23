# Code Generation — Questions (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Plan Approval

[Approval Fingerprint]: sha256:v3:68705fbaa19ee925f697ef6c0fcb3e3fa1c267fbf02c260c97a54fe291a37b94
[Planned Source]: b1b8b8329c56ecbb4f71dad16814b26e131422fe0b4d2d3df0741022758328d5

Plan revisado (iteración 2, re-trabajo de fidelidad visual; detalle en `code-generation-plan.md`): subir la fidelidad de la pantalla de Presupuesto al tema Angular + pulido iOS 26, con las 5 decisiones del propietario — D1 `BudgetRow` como **card** (superficie elevada, sombra, jerarquía, badges, etiquetas en mayúsculas); D2 **tab bar flotante Liquid Glass** subiendo el deployment target a **iOS 26** en `Package.swift`; D3 selector como **chip** con icono + recuadro en la navigation bar; D4 orden como **chip "Ordenar por: X ▾" bajo el título** (fuera de la topbar); D5 **logout en menú de ajustes (···)**. Puede ampliar el DesignSystem de F1 (token de elevación/sombra + estilo de card), coste 0 €. Mantiene consumo de U1, seguridad, estados, integración en `SplashView.case .resumed` y sesión F1 intacta. Checkpoint `cd ios && swift build && swift test` (87 tests verdes, sin regresión) + validación en iPhone 13 Pro.

- Approve Plan
- Request Changes

[Answer]: Approve Plan

## Consolidated Summary Confirmation

Checkpoint de U2 `u2-budget-ui` (estado final tras el re-trabajo de fidelidad + ampliación FR6):

- **Presupuesto**: cards neón-glass oscuras (saldo/rendimiento/puja máxima/premios, etiquetas en mayúsculas, badge de rendimiento), tema **oscuro global**, fondo deportivo neón (`Bundle.module`), tab bar flotante Liquid Glass (iOS 26), botones de toolbar **blancos** (trofeo selector / orden-sheet / ajustes ···).
- **Detalle de equipo (FR6, ampliación aprobada)**: navegación con zoom transition desde la card; hero colapsable; summary (saldo/gastado/ingresado) con `numericText`; Compras/Ventas como **menú glass en toolbar** siempre visible; filas de transacción con entrada **escalonada suave**; estados vacío/carga/error. U1 añade `Transaction`/`TeamDetailResponse` + `fetchTeamDetail` (mismo NetworkClient HTTPS, no-fuga).
- **Verificación**: `cd ios && swift build && swift test` = Build complete + **105 tests, 0 fallos** (94 + 11 FR6), sin regresión; compila para arm64 en dispositivo; validado en iPhone 13 Pro por el propietario.
- **Reviewer adversarial final**: READY (2 Minor advisory no bloqueantes).
- **Accesibilidad/contraste**: textos ≥4.5:1 sobre card oscura (validado con `ContrastRatio`), VoiceOver, Dynamic Type, Reduce Motion, signo como portador no-color.
- **Hallazgo registrado (deuda backend, fuera de alcance)**: el "saldo" difiere entre lista (`balance += prizes`) y detalle (sin prizes); es inconsistencia del backend, no de la app nativa; para intent de backend aparte.
- Sin dependencias nuevas; sesión F1 intacta.

¿Does this all look correct?

[Answer]: Looks correct
