# Code Quality Assessment — Futmondo Analytics

> Nota de cobertura (run 261018-design-system-nativo): el gate/CI y el backend no
> se reanalizaron en este escaneo enfocado; esa prosa se **preserva** del store
> previo (shallow). Lo nuevo de este run es la evaluación de calidad de la **capa
> de estilos / sistema de diseño** del frontend.

## Gate de CI (bloqueante)

El sistema tiene un **gate de CI bloqueante operativo** replicado en dos
workflows para cubrir PR y push directo:

- `.github/workflows/ci.yml` — job `quality`, disparo `pull_request → main`
  (required status check vía branch protection).
- `.github/workflows/fly-deploy.yml` — job `verify`, disparo `push → main`; los
  deploys dependen de él vía `needs:` (los `needs:` no cruzan workflows, por eso
  el gate se replica). Cadena: `verify → deploy-backend → deploy-frontend →
  smoke-test`.

Pasos bloqueantes verificados en **ambos** gates:

| Check | Herramienta | Nota |
|---|---|---|
| Secretos | gitleaks-action **@v3** (unificado) | Bloqueante desde el inicio |
| Lint backend | `ruff check .` (ruff **0.16.9** pin) | Promovido a bloqueante; sin `--fix` ni `ruff format` |
| Tests backend | `pytest -q --cov=app` con piso | `--cov-fail-under=27` (en `pytest.ini`) |
| Allowlist pip-audit | `scripts/check-allowlist-expiry.sh` | Entrada caducada vuelve a bloquear |
| Dep audit backend | `pip-audit` (entorno instalado, sin `-r`; pin **2.10.1**) | Bloquea findings CON fix; sin fix → allowlist versionada |
| Tests frontend | `ng test --watch=false` (Vitest) | Umbrales de cobertura dentro de `ng test` |
| Dep audit frontend | `npm audit --audit-level=high` | Trinquete de severidad solo endurece |

CI inyecta un `JWT_SECRET` efímero no productivo (`ci-ephemeral-secret-not-a-real-one`)
para que la app importe (fail-fast NFR1.1 en `config.resolve_jwt_secret`).

## Pisos de cobertura heredados (ratchet solo sube)

- **Backend**: `--cov-fail-under=27` (line-coverage total, sin `--cov-branch`),
  definido en `backend/pytest.ini`. Valor medido exacto sin margen (cobertura
  real ~27.52% al fijarlo). Reportado en paridad en `ci.yml` y el job `verify`.
- **Frontend**: `coverageThresholds` en `angular.json` (target `test`):
  `statements 19`, `branches 19`, `functions 17`, `lines 18`. Enforcement dentro
  de `ng test` (builder `@angular/build:unit-test`, runner Vitest), sin pasos
  extra ni `continue-on-error`.

Regla afirmada: NUNCA bajar/relajar un umbral para pasar el gate; el flapping se
arregla en el test no-determinista.

## Suite de tests existente

- **Backend** (`backend/tests/`): suite amplia **characterization-first** (~50+
  ficheros `test_*.py`). Cubre auth, integración/errores, dominio/sync/premios,
  con fixtures fake in-memory en `conftest.py` (SQLite), **sin red, sin DB real y
  sin credenciales/tokens reales** (gitleaks escanea también los tests).
- **Frontend** (`angular-app/src/**`): specs Vitest, incluidos los de auth
  (`auth.service.spec.ts`, `auth.interceptor.spec.ts`, `auth.guard.spec.ts`), más
  specs de servicios de feature (budget, stats, market, roster, sync, favorites,
  analytics, assistant, championship, evolution) e `idle-preloading-strategy.spec.ts`.

## Calidad de la capa de estilos / sistema de diseño (foco de este run)

Evaluación del tema Angular como fuente de verdad del diseño nativo:

### Señales positivas

- **Tema centralizado y tokenizado**: un único punto de entrada (`src/styles.scss`,
  declarado en `angular.json`) aplica Material 3 (`mat.theme`) y expone tokens de
  sistema `--mat-sys-*`; la mayoría de componentes/partials consumen esos tokens
  en lugar de colores crudos (buen punto de partida para derivar tokens nativos).
- **Tokens semánticos explícitos**: sección rotulada
  `// ===== DESIGN SYSTEM TOKENS =====` con color de dinero positivo/negativo,
  escala tipográfica (`h1`/`h2`/`h3`) y estilos de tabla; semántica clara y
  mapeable a estilos nativos.
- **Modo oscuro soportado**: Material gestiona el esquema y los overrides custom
  viven bajo `body.dark-theme` / `.dark-theme &`, lo que facilita un mapeo a
  `light`/`dark` en SwiftUI.
- **Partials organizados** (`shared/styles/` con `@forward`): primitivas
  reutilizables (tablas, tarjetas, grid responsive, estados de carga).
- **Consciencia móvil/PWA**: uso de `env(safe-area-inset-top)` (notch) y
  `padding-bottom` por home indicator — señales directamente portables a HIG.

### Deuda / riesgos de theming (a tener en cuenta al portar)

- **Colores hex hardcodeados** conviviendo con tokens `--mat-sys-*`: p. ej.
  `#4CAF50` en `.active-link` (`app.scss`), verdes del gradiente splash
  (`#1b5e20`/`#2e7d32`/`#43a047`), `#00C424`/`#14FF00` en badges
  (`_player-card.scss`). Al portar a nativo conviene consolidarlos como tokens de
  color semánticos en vez de valores sueltos.
- **`::ng-deep`** en `app.scss` (drawer, `router-outlet + *`): selector deprecado
  de Angular; no aplica en SwiftUI pero señala acoplamiento con internals de
  Material que no tendrán equivalente directo.
- **Modo oscuro parcial en custom**: `body.dark-theme` solo cubre clases propias;
  Material cubre el resto. El mapeo nativo debe reproducir ambos planos (tema del
  framework + overrides semánticos) para evitar inconsistencias.
- **Material 3 sin equivalente 1:1 en SwiftUI**: densidad (`density: 0`), ciertos
  tokens `--mat-sys-*` y comportamientos de componentes Material no tienen
  traducción directa; cubrir con Apple HIG (riesgo a documentar, no deuda del
  repo actual).

## Calidad de la capa nativa iOS (`ios/` — añadida por F1; foco del refresco F2)

Evaluación del paquete SwiftPM leído en este run:

### Señales positivas

- **Separación library/app testeable**: la lógica (Networking, Auth,
  DesignSystem puro) vive en `FutmondoKit`, cubierta por `swift test`; la UI
  SwiftUI vive en `FutmondoApp` tras `#if canImport(SwiftUI)`. El testTarget NO
  depende de la app, así que `swift test` compila en Linux/WSL sin SwiftUI.
- **Concurrencia estricta Swift 6**: `AuthService` es un `actor` (access token y
  refresh aislados); el refresh está **coalescido** (una sola tarea in-flight);
  `TokenHolder` usa `NSLock` portable. Contratos `Sendable` explícitos.
- **Manejo de errores tipado, sin credenciales**: `NetworkError`/`AuthError`/
  `KeychainError` son `Equatable` con payloads `Int`/`String`, nunca material de
  credencial (SEC-N4); el `init` del cliente rechaza base URL no-https (error
  propagado, no `precondition` eliminable por `-Ounchecked`).
- **Seguridad del refresh token**: solo en Keychain
  (`AfterFirstUnlockThisDeviceOnly`, sin iCloud sync); el access token solo en
  memoria; `LogoutFlagStore` persiste solo un booleano. Coherente con la regla
  afirmada "NUNCA almacenar la contraseña ni el refresh token en claro".
- **Accesibilidad**: componentes con `accessibilityIdentifier`, targets táctiles
  ≥44 pt, errores por icono+texto (no color solo), Dynamic Type, Reduce Motion.
- **Tests presentes**: `AuthServiceTests`, `NetworkClientTests`, `DesignSystemTests`.

### Deuda / riesgos (ya afirmados en memoria)

- **Cobertura de línea no medible en WSL/Linux**: `llvm-cov` no es fiable con el
  toolchain Swift en WSL; el piso de cobertura iOS NO se verifica numéricamente
  en WSL. Las vistas SwiftUI quedan fuera del cómputo (se validan en dispositivo).
- **Color Sets en código, no en asset catalog**: `actool` no está disponible en
  Linux/WSL, así que los tokens de color se definen en `DSColorToken`/
  `DSColorValue` (no `Assets.xcassets`); migración a asset catalog diferida a
  build en dispositivo con `xtool`.
- **`UserMe` mínimo (smoke F1)**: el modelo de usuario completo y los DTOs de
  datos (balances/championships) son trabajo de F2, aún no presentes.

## God-files como deuda conocida (NO ampliar) — backend (preservado)

Regla durable afirmada: NUNCA ampliar ni reescribir los god-files; el código
nuevo va tras una capa/función estrecha y testeable.

- `app/services/data_manager_v2.py` — ~33 KB observado en disco (ref. histórica
  ~166 KB; parte extraída a `data_manager/.../infrastructure/*_adapter.py`).
- `app/services/data_sync_service.py` — ~15 KB observado (ref. histórica ~84 KB).
- `app/services/assistant_service.py` (~2 KB; `I001`) y `photo_service.py`
  (~23 KB; `E722,F841` deuda afirmada Q6).

Patrón de SQL-en-router/endpoint también presente (p. ej. `auth/routes.py`,
`api/v1/endpoints/user.py`): deuda a no ampliar.

## Relevancia para el sistema de diseño nativo iOS (intent 261018)

- El tema está **bien centralizado y tokenizado**, lo que da una base sólida para
  derivar un sistema de tokens nativo (color, tipografía, superficies, modo
  claro/oscuro) a partir de `styles.scss`.
- Al portar: consolidar hex sueltos en tokens, mapear `--mat-sys-*` y
  `body.dark-theme` a `light`/`dark` nativos, y cubrir con HIG lo que Material 3
  no tenga 1:1.
- La suite frontend (Vitest/jsdom, specs que montan Material/CDK) **no porta 1:1**
  a un target nativo; el arnés de test de UI se rehace (riesgo a documentar).

## Sources

- `ios/Package.swift`, `ios/Sources/FutmondoKit/**/*.swift`, `ios/Sources/FutmondoApp/**/*.swift`
- `ios/Tests/FutmondoKitTests/*.swift`
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml` (store previo)
- `backend/pytest.ini`, `backend/ruff.toml`, `backend/.pip-audit-allowlist` (store previo)
- `angular-app/angular.json`, `angular-app/package.json`, `angular-app/eslint.config.js`
- `angular-app/src/styles.scss`, `angular-app/src/app/app.scss`, `angular-app/src/app/shared/styles/*.scss`
- `angular-app/src/app/features/login/login.component.ts`
- Listado de `backend/tests/` y `angular-app/src/app/core/**/*.spec.ts`

## Assumptions & Open Questions

- El porcentaje de cobertura actual no se recomputó en este escaneo; se reporta
  el **piso** configurado (backend 27, frontend 19/19/17/18) y el valor histórico
  (~27.52%) que motivó el piso backend. El gate/CI y el backend no se reverificaron
  en este run enfocado (prosa preservada / shallow).
- La catalogación completa de hex hardcodeados vs tokens no es exhaustiva: se
  listan los observados en los ficheros de estilo del foco (`styles.scss`,
  `app.scss`, `shared/styles/*`), no un barrido de toda `features/`.
