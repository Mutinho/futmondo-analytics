<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-18T14:06Z — Dos superficies (Q1=A): catálogo/preview (evidencia del sistema en claro/oscuro + Dynamic Type) y login de F1 revestido. Jerarquía del catálogo (Q3=A): Colores → Tipografía → Espaciado → Componentes. Login revestido fundamentado en el layout real de Angular (`login.component.ts`): card centrada sobre gradiente verde, logo+título+subtítulo, campo email con icono, campo contraseña con toggle, mensaje de error, botón primario con spinner.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-18T14:06Z — Accesibilidad (Q6=A): se incluye VoiceOver en los componentes base además de Dynamic Type + contraste, en vez de diferirlo; barato en SwiftUI y evita deuda en F2.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-18T14:06Z — Referencia de diseño = tema de Angular (`angular-app/src/styles.scss`); el mapeo exacto de roles Material 3 → SwiftUI y la escala tipográfica se concretarán en refined-mockups/diseño. Dispositivo de referencia iPhone 13 Pro (Q5=A).
