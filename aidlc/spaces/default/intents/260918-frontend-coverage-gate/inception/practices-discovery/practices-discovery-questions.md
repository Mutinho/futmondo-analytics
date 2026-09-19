# Practices Discovery — Preguntas de la entrevista

Intent: `frontend-coverage-gate` (FR10 cobertura de tests del frontend Angular + FR17.1 job `verify` con tests significativos). Brownfield, re-run. Solo se preguntan las decisiones de intención del equipo que el borrador del lead y las revisiones ciegas (quality/developer/devsecops) no pudieron establecer por evidencia.

---

## Q1 — Denominador de cobertura (el hueco clave que señaló la revisión de calidad)

Hoy `tsconfig.spec.json` incluye solo los `*.spec.ts` y la cobertura V8 por defecto mide **únicamente los archivos que ya tienen test**. Si fijamos un umbral así, el porcentaje **bajará** a medida que sembremos specs (más archivos entran al denominador), rompiendo el ratcheting. Hay que fijar el universo de cobertura ANTES de elegir un valor. ¿Qué política de denominador quieres?

- A. `coverage.all: true` + `coverage.include: src/app/**` con `coverage.exclude` explícito (specs, `main.ts`, `*.config.ts`, entornos, mocks). El umbral mide TODO el código de la app desde el principio (recomendado por calidad: el ratchet es honesto y no cae al sembrar).
- B. Medir solo los archivos tocados por tests (denominador estrecho), y ampliar el `include` por fases conforme se siembra.
- C. Decidir el `include`/`exclude` exacto más adelante en diseño; ahora solo afirmar que se usará `coverage.all: true` como principio.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Valor y forma del umbral inicial

El umbral es **ratcheting solo-hacia-arriba** (nunca se baja para pasar el gate). El valor inicial debe medirse DESPUÉS de sembrar los primeros specs, arrancando por debajo de la línea base medida para que el gate no se rompa al activarlo. ¿Cómo lo defines?

- A. Umbral **por métrica** (`lines`, `branches`, `functions`, `statements`), valor inicial medido tras la siembra, arrancando ligeramente por debajo de la línea base (recomendado por calidad).
- B. Un único umbral **global** de líneas, medido tras la siembra, arrancando por debajo de la base.
- C. Empezar el umbral en **0** al activar la infraestructura y subirlo en un MR posterior una vez sembrado.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Política de ratcheting (cómo sube el umbral)

- A. **Manual por MR**: subir el umbral a mano cuando la cobertura real supera el actual, revisado en la MR (simple, coste 0 €, control humano).
- B. **Semiautomático**: script/CI que sugiere el nuevo umbral pero requiere commit humano.
- C. **Automático**: CI reescribe el umbral al valor medido tras cada merge.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Alcance de la siembra inicial de specs (fase 1, antes de activar el umbral bloqueante)

La revisión de developer/calidad recomienda empezar por lo más testeable (puro, DI-friendly, sin red): `core/services/*`, `core/guards/auth.guard.ts`, `core/interceptors/auth.interceptor.ts`. ¿Qué alcance quieres para la fase 1?

- A. Solo capa `core/` crítica: servicios + `auth.guard` + `auth.interceptor` (lo más determinista; recomendado).
- B. `core/` crítica **más** un componente `features/*` de alto valor (p. ej. el diálogo de puja del mercado) para probar el patrón de test de componente standalone + signals + `HttpClient`.
- C. Barrido más amplio de `core/` + varios `features/*` en la fase 1.
- X. Other (please specify)

[Answer]: B

---

## Q5 — Dónde vive la config de cobertura y cómo se cablea el gate en CI

La revisión de developer corrige dos puntos del borrador: (1) la cobertura se configura en el **target `test` de `angular.json`** (opciones del builder `@angular/build:unit-test`), no en un `vitest.config` suelto; (2) la cobertura **no se hereda sola** — hoy `ci.yml` (PR) y el job `verify` de `fly-deploy.yml` (push→`main`) corren `ng test --watch=false` **sin** flag de cobertura, así que hay que fijar el comando exacto en **ambos**. ¿Cómo lo afirmas?

- A. Config de cobertura en el target `test` de `angular.json`; el gate se activa haciendo que `ng test` aplique el umbral, y se corrige el comando en `ci.yml` **y** en `verify` para que ambos ejerciten la cobertura (recomendado; una sola fuente de umbral, dos comandos alineados).
- B. Config en `angular.json`, pero cablear el umbral bloqueante solo en `ci.yml` (PR) por ahora; `verify` queda como deuda de pipeline (documentada).
- C. Mantener un `vitest.config` separado como fuente de la config de cobertura.
- X. Other (please specify)

[Answer]: A

---

## Q6 — Retirada de `skipTests` en los schematics de `angular.json` (FR10.1)

La revisión de developer/devsecops recomienda no quitarlo de los 8 schematics a ciegas. ¿Qué alcance quieres?

- A. Quitar `skipTests` en `service`, `guard`, `interceptor`, `class`, `component` (nacen con spec); **mantenerlo** en `pipe`, `resolver`, `directive` de bajo valor (recomendado).
- B. Quitar `skipTests` de **todos** los schematics (todo nace con spec).
- C. Quitar solo en `service`, `guard`, `interceptor` (la capa `core/` crítica) por ahora.
- X. Other (please specify)

---

[Answer]: A

## Q7 — Reglas duras a afirmar (Mandated/Forbidden) para este intent

Selecciona todas las que quieras afirmar como reglas duras (multi-selección):

- A. NEVER bajar/relajar un umbral de cobertura para pasar el gate — el ratcheting solo sube (candidato de devsecops/calidad; alineado con la prevención de sobreconfianza de `org.md`).
- B. ALWAYS verificar `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear cambios de devDependencies del frontend (ya afirmada; se reafirma).
- C. NEVER hardcodear secretos/tokens reales en specs; los tests de auth usan fakes/dobles (gitleaks escanea `*.spec.ts`) (candidato de devsecops G3).
- D. ALWAYS fijar versión exacta (pin) del proveedor de cobertura `@vitest/coverage-v8` (OSS, coste 0 €); nada de rangos abiertos en un gate bloqueante (candidato de devsecops G1).
- E. NEVER reintroducir `skipTests: true` en los schematics donde se retire (evita regresar a componentes sin spec).
- X. Other (please specify)

[Answer]: A, B, C, D, E

---

## Q8 — Deuda diferida (confirmar fuera de alcance)

La revisión confirma dos huecos que quedarían **diferidos** (documentados como deuda de pipeline, no cerrados por omisión): (1) la paridad de `--cov` de backend en el job `verify` (hoy `pytest -q` sin `--cov`); (2) SAST/DAST del frontend. ¿Confirmas que quedan fuera del alcance de este intent?

- A. Sí, ambos diferidos y documentados como deuda de pipeline (recomendado; este intent cierra solo la cobertura del frontend).
- B. Incluir la paridad `--cov` de backend en `verify` dentro de este intent.
- C. Incluir SAST/DAST del frontend dentro de este intent.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
