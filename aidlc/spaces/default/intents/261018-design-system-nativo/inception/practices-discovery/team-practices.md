# Team Practices — intent 261018-design-system-nativo (RE-RUN / DRAFT)

> Re-run de un proyecto brownfield MADURO (`futmondo-analytics`, en producción).
> Las prácticas ya están afirmadas en `aidlc/spaces/default/memory/team.md`; este
> draft las **reafirma** y añade únicamente el matiz que aporta este intent: el
> sistema de diseño / theming de la **app nativa iOS en SwiftUI** que reproduce,
> como fuente de verdad, el tema del frontend Angular existente.

## Way of Working

Mantenemos **trunk-based development** sobre `main` con ramas cortas y con
prefijo por tipo (`fix/...`, `chore/...`, `feat/...`, `docs/...`,
`feat(design)/...` para esta capa de diseño). La integración pasa por Pull
Request con **gate de CI obligatorio** (`.github/workflows/ci.yml`, disparo
`pull_request → main`, job `quality` como required status check); el push directo
a `main` re-ejecuta el gate en el job `verify` de `fly-deploy.yml` antes de
desplegar (los `needs:` no cruzan workflows, por eso el gate se replica).

- **Estrategia de merge**: **squash-merge** a `main`. Cada PR aterriza como un
  único commit sobre la historia lineal de `main`. Base de worktree `main`,
  destino `main`. (Línea base durable, alineada con `org.md`.)
- **Conventional Commits** con scope entre paréntesis y en castellano
  (`chore(aidlc)`, `docs(design)`, `feat(design)`…).
- **Matiz de ESTE intent (sistema de diseño nativo iOS)**: los entregables son
  **artefactos de diseño** (tokens de color/tipografía/superficies, mapeo
  Material 3 → SwiftUI, pantallas de referencia login + shell de navegación, modo
  claro/oscuro), **no** cambios de backend, de datos ni de CI/CD. No hay refactor
  del repo existente, ni promoción de linters/audits, ni trinquete de cobertura
  nuevo. Las ramas y commits de esta capa siguen la misma política trunk-based +
  squash-merge; el gate de CI aplica igual aunque el cambio sea de diseño/documental.

## Walking Skeleton

**No se ejecuta ceremonia de walking skeleton** para este intent (línea base
OFF). El sistema ya está **en producción** con un pipeline Fly.io maduro (región
`cdg`, dos apps `futmondo-api` + `futmondo-app`, healthcheck `/health`) y un
**gate de CI bloqueante ya operativo** (gitleaks + `ruff check` + `pytest` +
`pip-audit` + `ng test` + `npm audit`). Al ser un intent de **sistema de diseño**
cuyo insumo primario es la capa de estilos del `angular-app`, no hay ningún
componente ni pipeline que arrancar de cero: no se produce software ejecutable
nuevo que un esqueleto deba validar.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: este intent entrega **artefactos de diseño** (tokens y pantallas
  de referencia), no capas de software testeable, así que no introduce ningún
  piso de cobertura ni tests nuevos; la única obligación de testing es que la
  **suite existente siga en verde** (backend `pytest` + `pytest-cov` desde
  `backend/` con fixtures fake in-memory de `conftest.py`; frontend `ng test` con
  Vitest). Cuando SÍ se produzca código de UI, se implementa cada capa testeable
  y después se escriben y corren sus tests (test-after).
- **Methodology evidence**: posture test-after afirmada y vigente en memoria del
  equipo; la suite backend es **characterization-first** (~50+ `test_*.py`) y la
  frontend es Vitest sobre `@angular/build:unit-test`; ambas preexisten a este
  intent y no cambian por él.
- Un intent de diseño no modifica código de aplicación, por lo que no debería
  disparar fallos de la suite; pero el gate de CI corre igual en el PR y dentro de
  `ng test` el enforcement de cobertura (`coverageThresholds` en `angular.json`,
  `statements 19` / `branches 19` / `functions 17` / `lines 18`) es **bloqueante**:
  si un rojo aparece por **flapping** ajeno al cambio, se **arregla el test
  no-determinista**, NUNCA se baja un umbral/piso ni se añade `continue-on-error`
  (invariante del trinquete: sólo sube).
- **Matiz nativo iOS (riesgo a documentar en diseño, NO obligación de este
  intent)**: el arnés de test del frontend Angular (Vitest `4.1.11` +
  `@vitest/coverage-v8` + `jsdom`, specs que montan componentes Material/CDK) **no
  porta 1:1** a un target SwiftUI: no hay DOM/`jsdom` ni runner Angular CLI de
  Vitest, y una UI SwiftUI se verifica con el toolchain nativo de Apple
  (XCTest / previews / snapshot), no con Vitest/jsdom. Una eventual capa de UI
  nativa implicaría **rehacer el arnés de test de UI** y **re-basar** cualquier
  umbral sobre un runner distinto (suelo nuevo bajo tooling distinto, no un
  trinquete que suba), más una dimensión **E2E/dispositivo** (iPhone 13 Pro) hoy
  inexistente. El **backend no cambia** por una capa de diseño nativa (ni
  `pytest` ni el piso `--cov-fail-under=27`), para que nadie induzca trabajo
  backend inexistente.
- **No aplica en este intent**: los pisos de cobertura heredados (backend
  `--cov-fail-under=27`; frontend `19/19/17/18`) son estado del repo que este
  intent **no modifica**; no se induce trabajo de ratchet ni de paridad de señal.

## Deployment

**Desplegamos on-merge a `main`** hacia Fly.io (región `cdg`), sin entorno de
staging separado: el smoke test contra `/health` (5 reintentos, HTTP 200) es la
verificación del release (`.github/workflows/fly-deploy.yml`,
`verify → deploy-backend → deploy-frontend → smoke-test`). **Este intent es de
sistema de diseño y no despliega nada**: no toca la topología, el orden de
despliegue, los crons ni el gate `verify`. La política de despliegue se documenta
como línea base durable, no como trabajo a ejecutar.

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check
  `/health`) y frontend `futmondo-app` (nginx, check `/`). Base de datos **Neon
  PostgreSQL** (Frankfurt, tier free).
- **Secretos**: siempre vía `secrets` de GitHub Actions / Fly.io; en CI el
  `JWT_SECRET` es efímero y no productivo (`ci-ephemeral-secret-not-a-real-one`).
- **Rollback**: runbook documentado (`docs/ROLLBACK.md`); el mecanismo Fly.io es
  redeploy de la release anterior.
- **Restricción dura (durable) y su excepción acotada**: todo en **tiers
  gratuitos** — coste 0 € — para infraestructura, servicios y dependencias
  recurrentes. **Excepción aceptada y acotada**: el **coste de publicación de
  distribución nativa** (Apple Developer Program ~99 €/año) es una excepción
  conocida y bounded a ese mandato **sólo** para habilitar la distribución de la
  app nativa iOS. El sistema de diseño nativo de este intent se sostiene con el
  **SDK de Apple (coste 0 €)**, sin tooling de diseño de pago; el mandato de coste
  0 € sigue durable y sin relajar para todo lo demás.

## Code Style

Deferimos a las configuraciones del proyecto. **Este intent produce artefactos de
diseño** (tokens y pantallas de referencia), así que la mayor parte del estilo de
código aplica sólo si/cuando se genere código; se documenta como línea base
durable.

- **Idioma (durable)**: **identificadores, docstrings y comentarios en INGLÉS**;
  **texto de cara al usuario** (prosa de UI, strings visibles) y **mensajes de
  commit** (Conventional Commits con scope) en **CASTELLANO**. En este intent, la
  **prosa de los artefactos de diseño** va en castellano, conservando verbatim en
  inglés los tokens técnicos (`SwiftUI`, `Angular`, `Material 3`, `--mat-sys-*`,
  `Roboto`, claves/enums, rutas).
- **Fuente de verdad del diseño nativo**: el tema a reproducir es **Angular
  Material 3** del `angular-app` (`src/styles.scss`): primaria `mat.$green-palette`
  (verde), terciaria violeta, tipografía `Roboto`, modo claro/oscuro vía Material
  + `body.dark-theme`, y tokens semánticos propios (`money-positive` /
  `money-negative`, escala `h1`/`h2`/`h3`, gradiente de splash verde). El target
  nativo es **SwiftUI + SDK de Apple**; donde Material 3 no tenga equivalente 1:1
  (densidad, ciertos tokens `--mat-sys-*`, `::ng-deep`) se cubre con **Apple
  HIG**. **Google Stitch queda descartado** como referencia de diseño (decisión
  del propietario, 2026-10-18); la única fuente de verdad es el tema de Angular.
- **Linter/formato (durable, estado del repo)**: backend `ruff` (`ruff.toml`,
  `py312`, `line-length = 100`, `select = ["E","F","I"]`), `ruff check` bloqueante
  en ambos gates (pin `0.16.9`, sin `continue-on-error`). Frontend: ESLint flat
  config advisory/diferido; Prettier `3.8.1`. **NUNCA** `ruff format` masivo ni
  `--fix` de repo entero, ni Prettier masivo, sobre ficheros brownfield ya
  modificados (infla diffs, expone avisos preexistentes e invalida el pase de
  revisión en vuelo) — formatear sólo ficheros nuevos o de forma quirúrgica.
- **No aplica en este intent**: la promoción escalonada advisory→bloqueante, el
  saneamiento de deuda de lint por fichero y el pin de versiones de tooling del
  gate son trabajo de los intents de CI gate-hardening, **no** de un intent de
  diseño. No se toca `ci.yml`/`fly-deploy.yml`, `ruff.toml`, `pytest.ini` ni
  `angular.json`.
