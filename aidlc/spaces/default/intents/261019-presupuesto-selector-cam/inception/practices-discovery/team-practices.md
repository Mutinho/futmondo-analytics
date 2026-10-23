# Practices Discovery — Prácticas que gobiernan F2 `261019-presupuesto-selector-cam`

> Intent F2: feature nativa iOS SwiftUI — pantalla de **Budget** + **selector de
> championship**, brownfield, coste 0 €, tema Angular como fuente de verdad, sin
> cambios de backend. Este documento **confirma** qué prácticas ya afirmadas en
> `aidlc/spaces/default/memory/{team.md,project.md}` aplican a F2 y marca cada una
> como `ya afirmada (vigente)` o `nueva (propuesta a afirmar)`. No se re-inventan
> ni contradicen las reglas existentes.

## Resumen de gobernanza

F2 **hereda íntegramente** el set de reglas afirmado por los intents previos
(incluido F1 `261018-design-system-nativo`, que introdujo la capa nativa `ios/`).
No se detecta ninguna contradicción. La única práctica potencialmente "nueva"
—la estructura de testing/empaquetado iOS (`FutmondoKit` testeable + `FutmondoApp`
SwiftUI bajo `#if canImport(SwiftUI)`, validación en dispositivo)— **ya está
registrada** como Correction aprendida en `project.md` (learned 2026-10-19), por
lo que se confirma como vigente, no como novedad.

---

## 1. Way of Working / branching / merge — `ya afirmada (vigente)`

**Trunk-based development** sobre `main` con ramas cortas prefijadas por tipo
(`feat/...`, `feat(design)/...`, `fix/...`, `chore/...`, `docs/...`). Integración
por Pull Request con **gate de CI obligatorio** (`ci.yml` job `quality`, required
status check); el push directo a `main` re-ejecuta el gate en `fly-deploy.yml` job
`verify`. **Squash-merge**: cada PR aterriza como un único commit. Base de worktree
`main`, destino `main`.

*Aplicación a F2*: igual política; los entregables son código Swift nativo
(`ios/`) + artefactos de diseño, no backend ni CI. La rama/commits de F2 siguen
trunk-based + squash-merge.

## 2. Coste 0 € (mandato durable) — `ya afirmada (vigente)`

Sólo tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free). El
cliente nativo iOS se sostiene con el **SDK de Apple** (coste 0 €), sin tooling de
diseño de pago y con `dependencies: []` en `Package.swift`. **Excepción acotada**:
el coste de publicación de distribución nativa (Apple Developer Program ~99 €/año)
sólo para habilitar la distribución de la app.

*Aplicación a F2*: Budget + selector reutilizan Foundation/`URLSession` y SwiftUI
del SDK de Apple; no se prevé ninguna dependencia nueva.

## 3. Gate de CI bloqueante — `ya afirmada (vigente)`

gitleaks + `ruff check` + `pytest` (`--cov-fail-under=27`) + `pip-audit` +
`ng test` (Vitest, `coverageThresholds` 19/19/17/18) + `npm audit --audit-level=high`,
replicado en `ci.yml` (`quality`) y `fly-deploy.yml` (`verify`). **Ratchet solo
sube**; NUNCA bajar un umbral ni añadir `continue-on-error`; el flapping se arregla
en el test no-determinista.

*Aplicación a F2*: un feature nativo iOS no modifica backend ni frontend Angular,
así que no debería disparar fallos de la suite existente; el gate corre igual en el
PR y la suite existente debe **seguir en verde**. La cobertura de la capa iOS **no**
se suma a estos pisos (ver §6).

## 4. Política de idioma — `ya afirmada (vigente)`

**Identificadores, docstrings y comentarios en INGLÉS**; **texto de usuario y
mensajes de commit (Conventional Commits con scope) en CASTELLANO**. En los
artefactos de diseño/análisis, prosa en castellano con tokens técnicos verbatim en
inglés (`SwiftUI`, `FutmondoKit`, `#if canImport(SwiftUI)`, rutas, claves YAML).

*Aplicación a F2*: los nuevos símbolos Swift (p. ej. `BudgetView`,
`ChampionshipSelector`, DTOs de balances) en inglés; los strings de UI visibles y
commits en castellano.

## 5. Tema Angular Material 3 como fuente de verdad del diseño nativo — `ya afirmada (vigente)`

Reproducir en SwiftUI (SDK de Apple) el tema de `angular-app/src/styles.scss`
(primaria verde `mat.$green-palette`, terciaria violeta, `Roboto`, modo
claro/oscuro vía Material + `body.dark-theme`, tokens semánticos
`money-positive`/`money-negative`, escala `h1`/`h2`/`h3`, gradiente de splash
verde). Donde Material 3 no tenga equivalente 1:1, cubrir con **Apple HIG**.
**Google Stitch descartado** (decisión del propietario, 2026-10-18).

*Aplicación a F2*: Budget muestra saldos con los tokens `money-positive`/
`money-negative` ya definidos en `FutmondoKit.DSColorToken`; el selector de
championship usa los tokens de superficie/primaria existentes. F2 **consume** el
sistema de diseño F1, no lo rediseña.

## 6. Estructura y testing de la capa nativa iOS — `ya afirmada (vigente)` (Correction aprendida 2026-10-19)

Lógica pura y testeable en el target library **`FutmondoKit`**, cubierta con
`swift test` (XCTest); las vistas SwiftUI viven en el target de app **`FutmondoApp`**
guardadas con `#if canImport(SwiftUI)` y se validan **en dispositivo** (iPhone 13
Pro vía `xtool dev build`), fuera del cómputo de cobertura. Derivados del toolchain
WSL/Linux, ya afirmados:

- `actool` NO disponible en WSL → los Color Sets se definen **en código**
  (`DSColorToken`/`DSColorValue`), no en `Assets.xcassets`; `Package.swift` sin
  `resources` de asset catalog.
- `llvm-cov` **no fiable** en WSL → el piso de cobertura iOS no se verifica
  numéricamente en WSL; se cubre `FutmondoKit` con `swift test` y las vistas en
  dispositivo.

*Aplicación a F2*: la lógica de Budget (cálculo/formato de saldos, mapeo de DTOs,
selección de championship) va en `FutmondoKit` con XCTest; las `BudgetView` /
selector SwiftUI van en `FutmondoApp` bajo `#if canImport(SwiftUI)`, validadas en
dispositivo. El testTarget `FutmondoKitTests` sigue dependiendo **sólo** de
`FutmondoKit`.

## 7. Seguridad de credenciales (durable) — `ya afirmada (vigente)`

NUNCA almacenar la contraseña ni el refresh token Futmondo en claro. En el cliente
nativo el refresh token va a **almacenamiento seguro nativo** (iOS Keychain,
`AfterFirstUnlockThisDeviceOnly`), NUNCA a `ApplicationSettings`/`localStorage`; el
access token sólo en memoria. Las excepciones tipadas no incluyen material de
credencial en `message`/`repr`/`exc_info`.

*Aplicación a F2*: Budget/selector reutilizan la sesión y el `AuthService` ya
existentes; no introducen nuevo almacenamiento de credenciales ni exponen
secretos en errores.

## 8. Despliegue on-merge (durable, estado del repo) — `ya afirmada (vigente)`

Deploy on-merge a `main` hacia Fly.io (región `cdg`), smoke test contra `/health`.
F2 **no despliega nada nuevo** (feature de cliente nativo que reutiliza el backend);
se documenta como línea base durable, no como trabajo a ejecutar.

## 9. Metodología de testing: test-after — `ya afirmada (vigente)`

- **Methodology**: test-after
- **Ordering**: implementar cada capa testeable y después escribir y correr sus
  tests. La suite existente (backend `pytest` + frontend `ng test`) debe seguir en
  verde.

*Aplicación a F2*: la lógica de Budget en `FutmondoKit` se implementa y luego se
escriben sus `*Tests.swift` (test-after), como ya hace F1 (`AuthServiceTests`,
`NetworkClientTests`, `DesignSystemTests`).

## 10. No ampliar god-files / no refactor de oportunidad — `ya afirmada (vigente)`

NUNCA ampliar los god-files backend (`data_manager_v2.py`, `data_sync_service.py`,
`assistant_service.py`, `photo_service.py`) ni el patrón SQL-en-router. F2 es un
feature nativo iOS: **no toca backend**, así que la regla se cumple por
construcción; cualquier dato que necesite Budget se consume vía los endpoints
existentes sin ampliar esos ficheros.

---

## Práctica potencialmente nueva

**Ninguna nueva.** La estructura iOS `FutmondoKit`/`FutmondoApp` + validación en
dispositivo, que sería el único candidato razonable, **ya está capturada** en
`project.md` como Correction aprendida (2026-10-19) y se confirma aquí como
vigente para F2.

## Sources

- `aidlc/spaces/default/memory/team.md` (Way of Working, Testing Posture, Deployment, Code Style)
- `aidlc/spaces/default/memory/project.md` (Mandated / Forbidden / Corrections, incl. Corrections learned 2026-10-18 y 2026-10-19)
- `aidlc/spaces/default/memory/org.md` (trunk-based, squash-merge por defecto)
- `aidlc/spaces/default/codekb/futmondo-analytics/{technology-stack,code-quality-assessment,dependencies,code-structure}.md`
- `ios/Package.swift`, `ios/xtool.yml`
- `ios/Sources/FutmondoKit/DesignSystem/{DSColorValue,DSTypographyScale,ContrastRatio}.swift`
- `ios/Sources/FutmondoApp/DesignSystem/DSColor.swift`
- `ios/Tests/FutmondoKitTests/{DesignSystemTests,AuthServiceTests,NetworkClientTests}.swift`

## Assumptions & Open Questions

None.
