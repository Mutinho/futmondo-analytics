# Evidencia — Integración final (pipeline-deploy)

> Registro de las fuentes inspeccionadas y las inferencias realizadas, las
> contribuciones de los tres agentes de apoyo, las decisiones de la entrevista
> humana (Q1=B, Q2=B, Q3=C) y las notas de reenvío a stages posteriores, para los
> artefactos de la etapa Practices Discovery del intent
> `261006-angular-native-feasibili` (scope `classic`, análisis de viabilidad de
> Angular Native).

## Sources

Fuentes leídas completas en esta sesión (lead):

| Fuente | Ruta | Qué se extrajo |
|--------|------|----------------|
| Estado del intent | `aidlc/spaces/default/intents/261006-angular-native-feasibili/aidlc-state.md` | Scope `classic`, brownfield, stages to execute/skip, fase actual Inception |
| Prácticas afirmadas — equipo | `aidlc/spaces/default/memory/team.md` | Way of Working (trunk-based, squash-merge, Conventional Commits), Walking Skeleton (OFF), Testing Posture (test-after, pisos, paridad), Deployment (Fly.io on-merge, topología, cadena `needs:`), Code Style (ruff, ESLint diferido, idioma) |
| Prácticas afirmadas — proyecto | `aidlc/spaces/default/memory/project.md` | Reglas `## Mandated` (coste 0€, gate bloqueante, characterization-first, JWT_SECRET, …) y `## Forbidden` (no credenciales en claro, no god-file expansion, no ruff format masivo, no bajar cobertura, …); sección `## Corrections` (verificar frontend en container, reproducir pytest local, adaptar a Fly.io/Neon) |
| Reglas org-level | `aidlc/spaces/default/memory/org.md` | Way of Working (trunk-based default, squash-merge), Walking Skeleton (scope-dependent), Testing Posture (test-after default), Deployment (on-merge staging, production manual), Code Style (defer to project) |
| CodeKB — technology stack | `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md` | Angular 22 `^22.2.1`, Material 22 (DOM), Chart.js/`<canvas>`, Python 3.12, FastAPI, Neon, Fly.io, Vitest `4.1.11` pin, ESLint no instalado |
| CodeKB — architecture | `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md` | Monolito modular (SPA + API), contrato HTTP 59 ops, sesión híbrida access-en-memoria + refresh-en-cookie, diagrama Mermaid, diseño de capa reutilizable |
| CodeKB — dependencies | `aidlc/spaces/default/codekb/futmondo-analytics/dependencies.md` | Dependencias cruzadas angular-app↔backend (sólo contrato HTTP), portabilidad: servicios RxJS sí, componentes DOM/Material no |
| CodeKB — code quality | `aidlc/spaces/default/codekb/futmondo-analytics/code-quality-assessment.md` | Cobertura medida (backend 62 tests, piso `--cov-fail-under=27`; frontend 15 specs, umbrales en `angular.json`), ruff bloqueante, ESLint advisory, riesgos de portabilidad nativa (DOM, PWA/localStorage, Chart.js, sesión cookie), hallazgo `mat-sidenav` 12 items sin bottom-nav; cifras de god-files en `project.md` desactualizadas |
| CodeKB — code structure | `aidlc/spaces/default/codekb/futmondo-analytics/code-structure.md` | Organización del repo, paquetes `angular-app`/`backend`/`cron`/`proxy`, clasificación portable vs no-portable |
| CodeKB — business overview | `aidlc/spaces/default/codekb/futmondo-analytics/business-overview.md` | Dominio fantasy-football, funcionalidades, propósito, usuarios, contexto del intent activo |
| CI workflow | `.github/workflows/ci.yml` | **Fuente de verdad del gate**: gitleaks `@v3`, ruff `==0.16.9` bloqueante, pytest con `--cov`, pip-audit `==2.10.1`, ng test, npm audit `--audit-level=high` |
| Deploy workflow | `.github/workflows/fly-deploy.yml` | Job `verify` (réplica del gate), cadena `needs:` (verify→deploy-backend→deploy-frontend→smoke-test), gitleaks `@v3`, paridad con `ci.yml` |
| Pytest config | `backend/pytest.ini` | `addopts = -ra --cov-fail-under=27`, `pythonpath = .` |
| Ruff config | `backend/ruff.toml` | `py312`, `line-length=100`, `select=["E","F","I"]`, `per-file-ignores` god-files; cabecera **stale** (aún dice advisory) → deuda de documentación, no editada en este intent |
| Node version | `.nvmrc` | `22.22.3` |

[desc] Análisis de viabilidad de llevar Futmondo Analytics a una app nativa con Angular Native (NativeScript + Angular). Dispositivos objetivo: iPhone 13 Pro y Samsung A17. Evaluar: (1) menú inferior tipo 'liquid glass' con 4 opciones en iOS; (2) soporte de widgets (iOS y Android); (3) viabilidad general y encaje con el stack actual (Angular 22 PWA + FastAPI, Fly.io, Neon); (4) trazar una ruta de implementación. Intent de análisis, no de implementación.

### Contribuciones de los agentes de apoyo

- **aidlc-quality-agent** (inspeccionó: posture de testing, tooling de cobertura,
  gates de CI, `code-quality-assessment.md`, `angular.json`, `ci.yml`). Confirmó
  que la posture test-after y el invariante «el trinquete sólo sube» están bien
  portados como línea base durable y bien excluidos del alcance de un intent de
  análisis (sólo obligación: suite existente en verde). Aportó: (a) blindar que un
  rojo por **flapping** de cobertura en un PR documental se arregla reparando el
  test no-determinista, nunca bajando el umbral ni con `continue-on-error`;
  (b) hueco de calidad del propio análisis — la **portabilidad de la posture de
  testing** al target nativo (el builder Vitest/`jsdom` del frontend no existe en
  NativeScript → arnés de test de UI a rehacer, cobertura frontend a re-basar,
  dimensión E2E/dispositivo nueva; backend sin cambios); (c) usar las cifras de
  cobertura y de god-files **medidas en el scan**, no las de memoria.
- **aidlc-developer-agent** (inspeccionó: convenciones de nombres, fronteras de
  capa, manejo de errores, organización de ficheros, `code-structure.md`,
  `architecture.md`, `backend/ruff.toml`). Confirmó que las convenciones durables
  (idioma English/Castellano, no `ruff format` masivo brownfield, trunk-based +
  squash-merge + Conventional Commits) están bien capturadas y matizadas para un
  intent de prosa, y que las reglas de god-files, characterization-first,
  excepciones tipadas y CI gate-hardening están correctamente NO arrastradas.
  Aportó: (a) anclar la afirmación «`ruff check` bloqueante» a `ci.yml` (fuente de
  verdad) y anotar la cabecera **stale** de `backend/ruff.toml` como deuda de
  documentación sin editarla; (b) subir al cuerpo del análisis la **frontera de
  capa portable/no-portable** como criterio de diseño (ver abajo).
- **aidlc-devsecops-agent** (inspeccionó: reglas de seguridad y cadena de
  suministro, `ci.yml`/`fly-deploy.yml`, modelo de sesión, dependencias
  sensibles). Confirmó las reglas durables de seguridad (no secretos hardcodeados,
  gitleaks bloqueante en ambos gates, OSS pinned/coste 0 €, no password Futmondo
  en claro) y que la mecánica intent-específica (allowlist con caducidad, pins
  concretos, promoción escalonada, pisos de cobertura) está bien NO arrastrada.
  Aportó: (a) distinguir que el **escaneo de dependencias + secretos es un control
  de cadena de suministro durable del gate**, separado de la mecánica de
  promoción/allowlist/pin (base del Q2=B); (b) nota durable de que el refresh
  token debe ir a **almacenamiento seguro nativo** (Keychain/Keystore), nunca a
  `ApplicationSettings`/`localStorage` en claro, al perderse el aislamiento JS de
  la cookie `HttpOnly`; (c) insumos de riesgo para feasibility: superficie de
  cadena de suministro nativa (CocoaPods/Gradle no cubiertos hoy), firma de
  artefactos, `curl_cffi` como dependencia de nicho a mantener pinneada.

### Decisiones de la entrevista humana (fuente de verdad: `practices-discovery-questions.md`)

- **Q1 = B** — El coste de la cuenta de **Apple Developer (~99 €/año)** y la
  publicación de distribución nativa (Apple/Google) es una **excepción aceptada y
  acotada** al mandato de coste 0 €. Rationale: sin cuenta de desarrollador no hay
  distribución nativa posible a iPhone 13 Pro, luego tratarlo como factor
  excluyente invalidaría el análisis de entrada; se acepta como coste recurrente
  de distribución a documentar en feasibility, manteniendo coste 0 € durable para
  todo lo demás. → aterrizado como nota aclaratoria en la regla de coste 0 € de
  `discovered-rules.md` y en `## Deployment` de `team-practices.md`.
- **Q2 = B** — Se **eleva** el escaneo de dependencias (`pip-audit`/`npm audit`) y
  de secretos (`gitleaks`), ya bloqueante en ambos gates, a **control de cadena de
  suministro durable de equipo**, SEPARADO de la mecánica intent-específica
  (promoción escalonada, allowlist con caducidad, pin de versiones), que **no se
  arrastra**. Rationale: la *existencia* del escaneo bloqueante es un control
  permanente de seguridad, no un artefacto de un intent de CI concreto. → regla
  `ALWAYS` nueva en `## Mandated` de `discovered-rules.md`, redactada sin
  mencionar versiones, caducidad de allowlist ni pisos de cobertura.
- **Q3 = C** — Mezcla: el riesgo de **sesión / almacenamiento seguro nativo**
  (refresh token → iOS Keychain / Android Keystore, no en claro) entra como
  **riesgo central del propio análisis de viabilidad**; el **detalle del arnés de
  testing nativo** se **difiere** a un stage posterior. Rationale: el modelo de
  sesión condiciona la viabilidad y la garantía durable de no-credenciales-en-claro,
  así que es material de feasibility; el rediseño del harness de test es trabajo de
  diseño/implementación, no de la decisión de viabilidad. → el riesgo de sesión se
  refleja como regla durable de seguridad en `discovered-rules.md` e insumo de
  feasibility; el detalle de testing nativo queda como nota de reenvío (abajo).

### Criterio de diseño subido al análisis (frontera de capa)

La **clasificación portable vs no-portable** de `code-structure.md`/`dependencies.md`
es la frontera de capa más relevante para la ruta de implementación nativa y debe
figurar en el cuerpo del análisis como criterio de diseño, no sólo como evidencia:
`core/services/*` + `core/models/*` ≈ portables casi 1:1 (RxJS/signals, lógica de
dominio); `features/*` + `shared/*` **no portables** (atados a DOM/Material/plantillas
HTML). Corolario de arquitectura: migrar a nativo es **reemplazo de la capa de
presentación**, no un rewrite del backend (que permanece como capa de dominio
reutilizable detrás del contrato HTTP).

### Cifras medidas en el scan (no las de memoria)

Para dimensionar el esfuerzo de portar/rehacer, apoyarse en las cifras **medidas**:
`data_manager_v2.py` ~**33 KB / 685 líneas** (no «~166 KB» de `project.md`);
`assistant_service.py` ~**2 KB** (shim, no «~51 KB»). Cobertura medida: backend 62
tests con piso `--cov-fail-under=27`; frontend 15 specs con umbrales en
`angular.json` (statements 19 / branches 19 / functions 17 / lines 18) — estado
heredado que este intent no modifica.

### Notas de reenvío a stages posteriores (deferidas, fuera de este análisis)

- **Rediseño del arnés de testing nativo (Q3=C, diferido)**: definir el runner de
  frontend bajo NativeScript (p. ej. `@nativescript/unit-test-runner` + Karma/Jasmine
  o Mocha), re-basar el umbral de cobertura frontend sobre ese runner, e introducir
  testing **E2E/dispositivo** (iPhone 13 Pro / Samsung A17; p. ej. Appium /
  Detox / Playwright-mobile, coste 0 € con OSS). Pertenece a diseño/implementación,
  no a la decisión de viabilidad.
- **Superficie de cadena de suministro nativa (insumo devsecops)**: una futura
  migración necesitaría extender el escaneo de dependencias a los plugins nativos
  (CocoaPods / Gradle), hoy no cubiertos por `gitleaks`/`pip-audit`/`npm audit`.
- **Deuda de documentación**: la cabecera de `backend/ruff.toml` quedó stale (dice
  advisory cuando `ci.yml` ya lo corre bloqueante); corregirla fuera de este intent
  de análisis.

## Assumptions & Open Questions

None.
