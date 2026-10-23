# Team Practices — F3 Mercado (261020-mercado-pujas)

> **Naturaleza de esta etapa**: descubrimiento de **confirmación**, no de
> reinvención. Las prácticas del equipo ya están consolidadas y afirmadas en
> `aidlc/spaces/default/memory/team.md` y `project.md` (bajo `org.md`) por
> intents previos (F1 `261018-design-system-nativo`, F2
> `261019-presupuesto-selector-cam`, y los intents de backend/CI gate-hardening).
> Este documento resume las prácticas **vigentes** que aplican a F3 Mercado;
> no introduce prácticas nuevas. Prosa en castellano, tokens técnicos verbatim
> en inglés.

F3 Mercado es una **feature de UI nativa iOS (SwiftUI)** que reproduce la vista
Angular de Mercado como 2ª pestaña del `TabView` tras Presupuesto (F2), **sin
cambios de backend**, consumiendo `/api/v1/market/*` y
`/api/v1/sofascore/player/{name}`. La única novedad frente a F1/F2 es que F3
incluye **escritura** (pujar/cancelar) y un **2º endpoint externo** (Sofascore);
ambas **refuerzan** (no cambian) las prácticas de seguridad ya afirmadas.

## Way of Working (vigente — `team.md` / `org.md`)

- **Trunk-based development** sobre `main` con ramas cortas y prefijo por tipo
  (`feat/...`, `fix/...`, `chore/...`, `docs/...`). Para esta capa nativa aplica
  el prefijo de diseño/feature nativa ya usado en F1/F2.
- **Squash-merge** a `main`: cada PR aterriza como un único commit sobre la
  historia lineal. Base de worktree `main`, destino `main`.
- **Conventional Commits** con scope entre paréntesis y **en castellano**
  (p. ej. `feat(ios)`, `feat(market)`).
- Integración vía **Pull Request** con **gate de CI obligatorio**
  (`.github/workflows/ci.yml`, job `quality`, `pull_request → main`, required
  status check); el push directo a `main` re-ejecuta el gate en el job `verify`
  de `fly-deploy.yml` antes de desplegar.
- **Matiz de F3**: los entregables son **código nativo iOS** (vistas SwiftUI +
  lógica en `FutmondoKit`), **no** cambios de backend, datos ni CI/CD. No hay
  refactor del repo existente, ni promoción de linters/audits, ni trinquete de
  cobertura nuevo sobre backend/frontend; las ramas y commits siguen la misma
  política trunk-based + squash-merge.

## Walking Skeleton (vigente — `team.md`): **OFF**

No se ejecuta ceremonia de walking skeleton. El sistema ya está **en producción**
(Fly.io, dos apps `futmondo-api` + `futmondo-app`, healthcheck `/health`) con un
**gate de CI bloqueante operativo**. La capa nativa iOS (`ios/`, SwiftPM) ya
existe desde F1 y fue ampliada por F2: F3 **añade una pantalla** a un shell
`TabView` ya existente, no arranca ningún componente ni pipeline de cero. No hay
software ejecutable nuevo que un esqueleto deba bootstrap-ear.

## Testing Posture (vigente — `team.md` / `org.md`): **test-after**

- **Methodology**: test-after. **Ordering**: implementar cada capa testeable y
  después escribir y correr sus tests.
- **Matiz nativo iOS (ya afirmado)**: la **lógica pura y testeable** (networking,
  mapeo de DTOs de market, validación de importe de puja, ordenación) vive en el
  target library **`FutmondoKit`** y se cubre con **XCTest** ejecutable
  (`swift test`); las **vistas SwiftUI** (cards, banner, diálogo de puja, sheet
  Sofascore) van en el target de app bajo `#if canImport(SwiftUI)` y se
  **validan en dispositivo** (iPhone 13 Pro vía `xtool dev build`), quedando
  fuera del cómputo de cobertura.
- La **cobertura de línea (`llvm-cov`) NO es fiable con el toolchain Swift en
  Linux/WSL**: el piso de cobertura iOS no se verifica numéricamente en WSL
  (aprendizaje durable afirmado en `project.md`).
- **No aplica a F3**: los pisos de cobertura heredados de backend
  (`--cov-fail-under=27`) y frontend (`19/19/17/18` en `angular.json`) son estado
  del repo que F3 **no modifica**; la única obligación es que **la suite
  existente siga en verde** en el gate de CI.

## Deployment (vigente — `team.md` / `org.md`)

- **Deploy on-merge a `main`** hacia Fly.io (región `cdg`), sin staging separado;
  el smoke test contra `/health` es la verificación del release
  (`fly-deploy.yml`: `verify → deploy-backend → deploy-frontend → smoke-test`).
- **F3 no despliega nada nuevo**: no toca la topología, el orden de despliegue,
  los crons ni el gate `verify`. La app nativa iOS no se publica en este intent
  (distribución = excepción acotada **no activada**).
- **Secretos** siempre vía `secrets` de GitHub Actions / Fly.io; en CI el
  `JWT_SECRET` es efímero y no productivo.

## Code Style / Idioma (vigente — `team.md` / `project.md`)

- **Idioma (durable)**: **identificadores, docstrings y comentarios en INGLÉS**;
  **texto de cara al usuario** (strings visibles de la pantalla de Mercado) y
  **mensajes de commit** (Conventional Commits con scope) **en CASTELLANO**.
- **Linter/formato**: backend `ruff` (bloqueante, pin `0.16.9`) y frontend
  Prettier/ESLint aplican a sus respectivos subárboles; F3 toca `ios/` (Swift).
  **NUNCA** `ruff format` masivo ni `--fix` de repo entero ni Prettier masivo
  sobre ficheros brownfield ya modificados.
- **Coste 0 €**: F3 se sostiene con **SDK de Apple únicamente** (SwiftUI,
  Foundation/`URLSession`, Observation, Security/Keychain, XCTest); el paquete
  SwiftPM declara `dependencies: []`. Sin tooling de pago.
- **Color Sets en código, no en asset catalog**: `actool` no está disponible en
  Linux/WSL, así que los tokens de color se definen en código
  (`DSColorToken`/`DSColorValue`); migración a `Assets.xcassets` diferida.

## Fuente de verdad del diseño nativo (vigente — `team.md` / `project.md`)

- La **fuente de verdad del diseño** es el **tema Angular Material 3** del
  `angular-app` (`src/styles.scss`): primaria `mat.$green-palette` (verde),
  terciaria violeta, tipografía `Roboto`, modo claro/oscuro vía Material +
  `body.dark-theme`, y tokens semánticos propios (`money-positive`/
  `money-negative`, escala `h1`/`h2`/`h3`, gradiente de splash verde). El target
  nativo es **SwiftUI + SDK de Apple**; donde Material 3 no tenga equivalente 1:1
  se cubre con **Apple HIG**. **Google Stitch** queda descartado (decisión del
  propietario, 2026-10-18).
- La **fuente de verdad del comportamiento** de la pantalla de Mercado es la
  vista Angular `angular-app/src/app/features/market/` (reproducción 1:1 de
  campos de card, banner, selector de orden, diálogo de puja min/max y detalle
  Sofascore).

## Seguridad reforzada por la novedad de F3 (ya afirmada, NO nueva)

- **Escritura (pujar/cancelar)**: `POST /market/bid` y `POST /market/cancelbid`
  son endpoints autenticados que viajan con `Authorization: Bearer <access
  token>`; el access token vive **solo en memoria** y el refresh token **solo en
  Keychain** (`AfterFirstUnlockThisDeviceOnly`, sin iCloud sync) — regla afirmada
  "NUNCA almacenar la contraseña ni el refresh token en claro".
- **2º endpoint (Sofascore)**: consumo de solo lectura; los errores de
  integración se exponen como fallo tipado **sin material de credencial** en
  mensaje/`repr`/`exc_info` (regla afirmada de no-credenciales-en-claro).

## Sources

- `aidlc/spaces/default/memory/org.md` (way of working, testing posture,
  deployment, code style, conversation language).
- `aidlc/spaces/default/memory/team.md` (way of working, walking skeleton OFF,
  testing posture test-after, deployment Fly.io, code style/idioma, fuente de
  verdad del diseño nativo, excepción acotada Apple Developer Program).
- `aidlc/spaces/default/memory/project.md` (coste 0 €, gate CI bloqueante,
  secretos/JWT_SECRET, god-files no-ampliar, aprendizajes Swift/WSL:
  Color Sets en código, cobertura `llvm-cov` no fiable → `FutmondoKit` + XCTest).
- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md`,
  `dependencies.md`, `code-quality-assessment.md`, `architecture.md`,
  `business-overview.md` (evidencia del repo).
- `.../ideation/intent-capture/intent-statement.md`,
  `.../ideation/scope-definition/scope-document.md` (alcance F3).

## Assumptions & Open Questions

None.
