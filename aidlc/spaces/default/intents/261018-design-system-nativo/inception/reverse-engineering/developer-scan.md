# Developer Code Scan — Focused (Sistema de diseño nativo iOS)

Intent: `261018-design-system-nativo`. Escaneo **enfocado** del tema del
frontend Angular como **fuente de verdad del diseño** para reproducirlo en una
app nativa iOS (SwiftUI). Proyecto brownfield `futmondo-analytics` (repo raíz,
sin repos registrados). Profundidad: Standard. Modo: pipeline, LEAD-ONLY
(el developer escanea y sintetiza los 9 artefactos).

## Developer Code Scan Results

### Scan Coverage

#### Analyzed deeply (leído y entendido)

- `angular-app/src/styles.scss` — **fuente de verdad del tema**: `mat.theme()`
  con `primary: mat.$green-palette`, `tertiary: mat.$violet-palette`, tipografía
  `Roboto`, `density: 0`; tokens semánticos `money-positive` (#2e7d32) /
  `money-negative` (#d32f2f); escala tipográfica `h1` 28/700, `h2` 20/600, `h3`
  16/600; estilos globales de tabla Material; fondo splash
  `linear-gradient(135deg, #1b5e20 → #2e7d32 → #43a047)`; overrides de modo
  oscuro bajo `body.dark-theme` (money-positive #66bb6a, money-negative #ef5350).
- `angular-app/src/app/app.scss` — layout del shell: sidebar (`.app-sidenav`
  250px, mini-mode tablet 64px), toolbar móvil sticky, `.page-content`, estado
  activo de navegación (`.active-link` #4CAF50 + texto blanco), `env(safe-area-inset-top)`
  para notch iPhone, animación de transición de ruta `fadeIn`, responsive
  (<768px con `padding-bottom: 80px` por home indicator; 769–1024px sidebar mini).
- `angular-app/src/app/features/login/login.component.ts` — **componente de login
  de referencia** (standalone, Material): `mat-card` centrada (max-width 400px,
  border-radius 16px) sobre el gradiente verde de splash; campos
  `appearance="outline"` con `matPrefix` (email/lock) y toggle de visibilidad de
  contraseña; botón `mat-flat-button color="primary"` full-width con spinner;
  bloque de error con fondo `#ffebee`/texto `#d32f2f`; usa signals
  (`loading`/`error`) y `AuthService.login`.
- `angular-app/src/app/core/` (escaneo profundo del subárbol del intent):
  - `services/auth.service.ts` — access token **solo en memoria**, user en
    `localStorage` (no el token), refresh por cookie (`withCredentials`),
    `tryRecoverSession`.
  - `interceptors/auth.interceptor.ts` — `Authorization: Bearer`, `withCredentials`
    en `/auth/*`, reintento con refresh en 401 (cola `BehaviorSubject`), logout en 403.
  - `guards/auth.guard.ts` — `CanActivateFn`: recupera sesión / redirige a `/login`.
  - `services/championship.service.ts` — selección de campeonato activo (signals,
    `localStorage`), fallback `/api/v1/user/championships` → `/api/v1/championships`.
  - `preloading/idle-preloading-strategy.ts` — precarga lazy diferida por
    inactividad (`requestIdleCallback` + fallback `setTimeout`), BR3.1/BR3.3/NFR4.
  - `models/` — `stats.model.ts`, `budget.model.ts`, `evolution.model.ts` (DTOs).
  - resto de `services/*.service.ts` (analytics, budget, stats, market, roster,
    sync, favorites, assistant, evolution) — consumidores de `/api/v1/*`.
- `angular-app/angular.json` — builders `@angular/build:*`, estilos globales
  `src/styles.scss`, `inlineStyleLanguage: scss`, target `test` con runner
  `vitest` y `coverageThresholds` (statements 19 / branches 19 / functions 17 /
  lines 18); budgets de build (`anyComponentStyle` warn 8kB / error 12kB).
- Apoyo del sistema de diseño (dentro del árbol del intent): `src/app/shared/styles/`
  (`_index.scss`, `_table-common.scss`, `_player-card.scss`, `_responsive-grid.scss`,
  `_loading-states.scss`) y `src/app/app.config.ts` (wiring de interceptor,
  preloading y service worker).

#### Skimmed only (ojeado, sin lectura profunda)

- `angular-app/src/app/features/` (resto de features: budget, market, finances,
  calculator, transactions, my-roster, favorites, clausulable, classification,
  evolution, stats, settings, analytics, splash) — inventario por nombre.
- `angular-app/src/app/shared/components/` — componentes compartidos (player-card,
  badges Sofascore/starter, view-toggle, loading-state, page-header, assistant-*)
  por nombre; se leyeron solo los partials de `shared/styles/`.
- `angular-app/src/app/core/**/*.spec.ts` — specs Vitest (inventario por nombre).

#### Left out (no abierto)

- Todo el backend (`backend/`): fuera del alcance de un intent de theming nativo
  (el tema no depende del backend). Permanece como cobertura **shallow** heredada
  del store previo (no re-verificable en este run).
- `.github/workflows/`, `docs/`, `cron/`, `proxy/`, `spikes/`, `scripts/`:
  fuera del foco de diseño.
- Instalación de AI-DLC (`.kiro/`, `.claude/`, `.codex/`, `.cursor/`, `.aidlc/`,
  `aidlc/`) y secciones AI-DLC de `AGENTS.md`/`.gitignore`: excluidas por regla.
- Build outputs / deps / caches (`node_modules/`, `.angular/`, `dist/`,
  `coverage/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`): omitidos por
  `.gitignore` y "What to Skip".

### Packages Found

- `angular-app` — application — TypeScript/Angular 22 — PWA frontend (fuente del
  tema de diseño). (El resto del monorepo no se re-analiza en este run enfocado.)

### Build System

- **Type**: `@angular/build` (Angular CLI) + npm.
- **Config Files**: `angular-app/angular.json`, `angular-app/package.json`,
  `angular-app/tsconfig*.json`.
- **Build Dependencies**: estilos globales `src/styles.scss`;
  `inlineStyleLanguage: scss`; schematics de componentes con `style: scss`.

### APIs Discovered

- Ninguna nueva en el foco de diseño. El `core/` consume `/auth/*` y `/api/v1/*`
  (documentado ya en `api-documentation.md`); sin cambios de contrato en este run.

### Frameworks & Libraries

- Angular 22 (standalone + signals) — framework de UI.
- Angular Material + CDK 22 — sistema de diseño base (Material 3 vía `mat.theme`).
- SCSS — lenguaje de estilos (tokens `--mat-sys-*`).

### Test Coverage

- **Test Directories**: `angular-app/src/app/**/*.spec.ts` (co-ubicados).
- **Test Frameworks**: Vitest (builder `@angular/build:unit-test`).
- **Coverage Config**: presente — `coverageThresholds` en `angular.json`
  (statements 19 / branches 19 / functions 17 / lines 18).

### Code Quality Indicators

- **Linting**: ESLint flat config (`eslint.config.js`) advisory/diferido;
  Prettier 3.8.1.
- **CI/CD**: gate bloqueante (`ng test` con umbrales) — no modificado por este intent.
- **Documentation**: SCSS bien comentado; `styles.scss` marca explícitamente
  `// ===== DESIGN SYSTEM TOKENS =====`.

### Technical Debt Signals

- Uso de `::ng-deep` en `app.scss` (drawer/router-outlet) — selector deprecado de
  Angular; a tener en cuenta si se porta el layout, pero no aplica en SwiftUI.
- Colores hex hardcodeados conviviendo con tokens `--mat-sys-*` (p. ej. `#4CAF50`
  en `.active-link`, `#00C424` en badges, verdes del gradiente splash): al portar
  a nativo conviene consolidarlos como tokens de color semánticos.
- `body.dark-theme` cubre solo clases custom; Material gestiona el resto del modo
  oscuro — el mapeo nativo debe cubrir ambos planos.

## Handoff Summary

- **Intent-relevant finding**: El tema de diseño vive centralizado en
  `angular-app/src/styles.scss` (Material 3: primaria **verde** `mat.$green-palette`,
  terciaria **violeta** `mat.$violet-palette`, tipografía **Roboto**, claro/oscuro
  vía `body.dark-theme`) más los tokens semánticos propios
  (`money-positive`/`money-negative`, escala `h1`/`h2`/`h3`, gradiente de splash
  verde `#1b5e20→#2e7d32→#43a047`). El login (`login.component.ts`) y el shell
  (`app.scss`) son las referencias concretas de aplicación de ese tema
  (tarjeta sobre gradiente, outline fields, `.active-link` verde). Esta es la
  **fuente de verdad** que la app nativa iOS debe reproducir con SDK de Apple
  (coste 0 €), cubriendo con Apple HIG donde Material 3 no tenga equivalente 1:1.
- **Risks / follow-up**:
  - El runner Vitest/jsdom y los specs que montan componentes Material/CDK **no
    portan 1:1** a un target nativo; el arnés de test de UI se rehace si hay
    migración nativa (riesgo a documentar, no trabajo de este intent).
  - Donde Material 3 no tiene equivalente directo en SwiftUI (densidad, tokens
    `--mat-sys-*`, `::ng-deep`), cubrir con Apple HIG sin dependencias de pago.
  - Google Stitch queda descartado como referencia (decisión del propietario,
    2026-10-18): la única fuente de verdad del diseño es el tema de Angular.
