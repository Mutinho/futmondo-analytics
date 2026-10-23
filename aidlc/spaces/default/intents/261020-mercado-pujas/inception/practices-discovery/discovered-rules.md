# Discovered Rules — F3 Mercado (261020-mercado-pujas)

> Prosa en castellano, tokens técnicos verbatim en inglés.

## Resultado del descubrimiento

**No hay ninguna regla NUEVA que proponer a memoria.** F3 Mercado es una feature
de UI nativa iOS que **reproduce una pantalla existente** y **reutiliza** la base
de F1/F2 sin cambios de backend. Todas las prácticas aplicables ya están
**afirmadas y consolidadas** en `org.md`, `team.md` y `project.md` por intents
previos (F1 `261018-design-system-nativo`, F2 `261019-presupuesto-selector-cam`,
y los intents de backend/CI gate-hardening de 2026-09).

La única novedad de F3 frente a F1/F2 — **escritura** (pujar/cancelar) y un
**2º endpoint externo** (Sofascore) — **refuerza** las reglas de seguridad ya
afirmadas; **no** las cambia ni exige reglas nuevas. Proponer cualquier regla que
se desvíe de la política más amplia (`org → team → project`) sería rechazado en
el gate de admisión de memoria, por lo que este intent **no propone afirmar
nada**.

## Reglas vigentes relevantes — CONFIRMADAS (ya afirmadas, NO nuevas)

Las siguientes reglas aplican directamente a F3 y se **confirman como vigentes**.
Se escriben en formato `ALWAYS`/`NEVER` solo para legibilidad; **todas están
YA-AFIRMADAS** en memoria y **ninguna se propone como nueva**.

### Way of working / deployment

- [YA-AFIRMADA] ALWAYS mantener **trunk-based + squash-merge** a `main` con
  **Conventional Commits** con scope en castellano (fuente: `team.md`/`org.md`
  `## Way of Working`).
- [YA-AFIRMADA] ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `ruff
  check` + `pytest` + `pip-audit` + `ng test` + `npm audit`) antes de fusionar a
  `main`; un rojo nunca llega a producción (fuente: `project.md`/`team.md`).
- [YA-AFIRMADA] NEVER tocar la topología de despliegue, el orden
  `verify → deploy-backend → deploy-frontend → smoke-test` ni el gate `verify` en
  un intent que no es de CI/CD (fuente: `team.md` `## Deployment`).

### Coste y dependencias

- [YA-AFIRMADA] ALWAYS mantener el proyecto a **coste 0 €**: F3 se sostiene con
  **SDK de Apple únicamente** (`dependencies: []` en `ios/Package.swift`); sin
  tooling ni librerías de pago. La excepción acotada (Apple Developer Program)
  **no se activa** en F3 (fuente: `team.md`/`project.md` `## Mandated`;
  scope-document "Distribución fuera de alcance").

### Testing (posture nativo iOS)

- [YA-AFIRMADA] ALWAYS colocar la **lógica pura testeable** en `FutmondoKit` y
  cubrirla con **XCTest** (`swift test`); las vistas SwiftUI van bajo
  `#if canImport(SwiftUI)` en `FutmondoApp` y se validan en dispositivo, fuera
  del cómputo de cobertura (fuente: `project.md` `## Corrections`, aprendizaje
  2026-10-19).
- [YA-AFIRMADA] NEVER verificar numéricamente el piso de cobertura iOS con
  `llvm-cov` en Linux/WSL (no fiable); la validación de UI es en dispositivo
  (fuente: `project.md` `## Corrections`, aprendizaje 2026-10-19).
- [YA-AFIRMADA] ALWAYS exigir que la **suite existente siga en verde**
  (backend `pytest`, frontend `ng test`); NEVER bajar/relajar un umbral o piso de
  cobertura para pasar el gate — el ratchet sólo sube; el flapping se arregla en
  el test no-determinista (fuente: `project.md`/`team.md`/`org.md`).

### Diseño (fuente de verdad)

- [YA-AFIRMADA] ALWAYS reproducir en **SwiftUI** (solo SDK de Apple) el tema
  **Angular Material 3** (`angular-app/src/styles.scss`) como fuente de verdad
  del diseño nativo; donde Material 3 no tenga equivalente 1:1, cubrir con
  **Apple HIG**. Google Stitch descartado (fuente: `project.md`/`team.md`,
  2026-10-18).
- [YA-AFIRMADA] ALWAYS definir los **Color Sets en código**
  (`DSColorToken`/`DSColorValue`), no en `Assets.xcassets` (`actool` no
  disponible en WSL); migración a asset catalog diferida (fuente: `project.md`
  `## Corrections`, 2026-10-19).

### Seguridad (reforzada por la escritura y el 2º endpoint de F3)

- [YA-AFIRMADA] NEVER almacenar la contraseña Futmondo ni el refresh token en
  claro: el refresh token va a **almacenamiento seguro nativo** (iOS Keychain,
  `AfterFirstUnlockThisDeviceOnly`, sin iCloud sync); el access token solo en
  memoria. Las peticiones de escritura (`POST /market/bid`,
  `POST /market/cancelbid`) viajan con `Authorization: Bearer` reutilizando ese
  modelo (fuente: `project.md` `## Forbidden`).
- [YA-AFIRMADA] NEVER incluir material de credencial (password, token) en el
  mensaje, `repr` o `exc_info` de una excepción de integración; los errores de
  los endpoints de Mercado y de Sofascore se exponen como **fallo tipado** con
  contexto no sensible (status, endpoint) (fuente: `project.md` `## Forbidden`,
  2026-09-24).
- [YA-AFIRMADA] NEVER usar un `JWT_SECRET` por defecto en producción; el arranque
  del servicio web exige un secreto no-default (NFR1.1) — invariante del backend
  que F3 no modifica pero preserva al consumir `/api/v1/*` (fuente:
  `project.md`/`team.md`).

### Idioma

- [YA-AFIRMADA] ALWAYS usar **identificadores, docstrings y comentarios en
  INGLÉS** y **texto de usuario / mensajes de commit en CASTELLANO**
  (Conventional Commits con scope). Los strings visibles de la pantalla de
  Mercado van en castellano (fuente: `org.md`/`team.md`/`project.md`).

### Brownfield (no-ampliar god-files)

- [YA-AFIRMADA] NEVER ampliar los god-files existentes del backend
  (`data_sync_service.py`, `data_manager_v2.py`, `assistant_service.py`,
  `photo_service.py`) ni el patrón SQL-en-router. **No aplica directamente a F3**
  (que no toca backend), pero se confirma como invariante del repo por si surge
  tentación de "arreglar de paso" (fuente: `project.md` `## Forbidden`).

## Sources

- `aidlc/spaces/default/memory/org.md`, `team.md`, `project.md` (reglas
  afirmadas: way of working, deployment, coste 0 €, testing posture, diseño,
  seguridad, idioma, brownfield).
- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md`,
  `dependencies.md`, `code-quality-assessment.md` (evidencia: `dependencies: []`,
  `FutmondoKit`/XCTest, Keychain, Color Sets en código, gate CI).
- `.../ideation/scope-definition/scope-document.md`,
  `.../ideation/intent-capture/intent-statement.md` (alcance F3: escritura +
  Sofascore, distribución fuera de alcance).

## Assumptions & Open Questions

None.
