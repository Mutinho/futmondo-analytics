**Collaborator:** aidlc-devsecops-agent

## Contribution

Inspección ciega del borrador del lead desde la lente DevSecOps (lint/format, SAST/DAST,
escaneo de secretos y dependencias, cadena de suministro), acotada a lo que ESTE intent
cambia: añadir un proveedor de cobertura de frontend + un umbral de cobertura bloqueante.

### 1. Cadena de suministro — nueva devDependency `@vitest/coverage-v8`

- **Pin exacto, no rango.** El borrador propone añadir `@vitest/coverage-v8` como
  devDependency, pero `angular-app/package.json` hoy usa rangos flotantes (`^`/`~`) en todo
  el bloque `devDependencies`. Para la nueva dependencia de cobertura debe **fijarse la
  versión exacta** (sin `^`/`~`) o, como mínimo, **alinear su MAJOR/MINOR con `vitest ^4.0.8`**
  (el proveedor de cobertura de Vitest debe casar con la versión del runner: `@vitest/coverage-v8`
  4.x para `vitest` 4.x). Un rango abierto en la herramienta que MIDE el gate de calidad es
  superficie de suministro innecesaria en un gate bloqueante.
- **Paquete OSS conocido, sin typosquat.** `@vitest/coverage-v8` es el paquete oficial del
  scope `@vitest` (mismo publisher que `vitest`, ya presente y confiado en el repo). Es la
  opción de menor riesgo de suplantación frente a alternativas de tercero; `istanbul` puro
  también es OSS legítimo pero introduce un publisher distinto. Recomiendo `@vitest/coverage-v8`
  precisamente por proceder del mismo scope ya auditado. La entrevista (Q6) debe cerrar el
  proveedor, pero desde la lente de cadena de suministro `@vitest/coverage-v8` es la elección
  segura por defecto.
- **Lockfile y `npm audit` (advisory) cubiertos.** `angular-app/package-lock.json` está
  commiteado y ambos caminos de CI usan `npm ci` (instalación determinista contra el lock),
  así que el hash del nuevo árbol queda anclado. `npm audit --audit-level=high` corre advisory
  en `ci.yml`: la incorporación NO puede introducir un CVE High silencioso sin que el paso lo
  reporte, aunque no bloquee. La regla ya afirmada de verificar `npm ci` + `ng test` en
  `node:22.22.3` antes de pushear cubre el riesgo de romper el gate al mutar el lock. Correcto.
- **Coste 0 €.** `@vitest/coverage-v8` es OSS puro, sin servicio/proveedor de pago (no es
  Codecov/Coveralls de pago). El reporte de cobertura se genera y consume dentro del propio
  `ng test` en el runner de GitHub Actions (free tier). Cumple el mandato de coste 0 €.

### 2. Integridad del gate — el bloqueante NO se debe debilitar

- **Confirmo que el borrador PRESERVA el gate.** El diseño de "activar el umbral dentro de
  `ng test` para que `ci.yml` y `verify` lo hereden" NO toca los pasos existentes de
  `pytest`/gitleaks ni les añade `continue-on-error`. La exigencia de cobertura entra como un
  fallo interno de `ng test` (exit != 0), que ya es un paso BLOQUEANTE en ambos workflows.
  Añadir señal a un paso que ya bloquea es aditivo y no relaja nada. Correcto.
- **gitleaks sigue bloqueante en ambos caminos — VERIFICADO.** En `.github/workflows/ci.yml`
  el paso `Secret scan (gitleaks)` usa `gitleaks/gitleaks-action@v3` sin `continue-on-error`
  (bloquea el PR). En `.github/workflows/fly-deploy.yml` el paso homólogo usa
  `gitleaks/gitleaks-action@v2` sin `continue-on-error` dentro del job `verify`, del que
  dependen los deploys vía `needs:`. Este intent NO modifica ninguno de esos dos pasos, así
  que la paridad de escaneo de secretos (@v3 PR / @v2 verify, ambos bloqueantes) se mantiene
  intacta. Confirmado.
- **Riesgo a vigilar (entrevista Q4).** El único vector de debilitamiento sería que el humano
  pidiera un "paso explícito de reporte de cobertura" y este se cableara con
  `continue-on-error: true` (como los pasos advisory de ruff/ESLint/audit), dejando el gate
  real sin el umbral. La regla debe ser clara: el umbral se aplica DENTRO de `ng test`
  (bloqueante); cualquier paso adicional de reporte es solo observabilidad, nunca el enforcement.

### 3. Trinquete (ratcheting) como restricción DURA — CONFIRMO

- La regla candidata `NEVER bajar ni relajar un umbral de cobertura para hacer pasar el gate`
  pertenece a `## Forbidden` como restricción dura, no como preferencia blanda. Bajar un
  umbral para que el gate pase en verde es exactamente el patrón de "relajar el control de
  calidad para tapar un rojo": convierte un gate de calidad en decorativo y encaja con la
  prevención de exceso de confianza de `org.md` (no debilitar un control para forzar un pase).
  La resolución de un rojo de cobertura es **añadir tests**, no bajar el piso.
- La regla hermana `NEVER fijar un umbral inicial por encima de la cobertura real de la línea
  base` también es dura y correcta: fijar el piso por encima de la realidad rompería el gate
  bloqueante de inmediato y forzaría precisamente la relajación que la regla anterior prohíbe.
  Ambas son coherentes entre sí y con el mandato de gate bloqueante ya afirmado.

### 4. Huecos de seguridad / cadena de suministro que la ENTREVISTA debe resolver

- **G1 — Versión exacta del proveedor de cobertura.** Fijar `@vitest/coverage-v8` a versión
  exacta (o al menos casada con `vitest` 4.x) y registrarlo en `discovered-rules.md`. Hoy el
  borrador no fija la política de pin para la nueva dependencia.
- **G2 — SAST/DAST fuera de alcance (documentar diferimiento).** Este intent NO introduce
  SAST (semgrep/CodeQL) ni DAST; el frontend no tiene análisis estático de seguridad más allá
  de ESLint advisory. No es objetivo de este intent y su ausencia es preexistente, pero debe
  quedar registrada como deuda de pipeline (no cerrada por omisión), igual que la paridad
  `--cov` de backend en `verify`.
- **G3 — El umbral no debe crear presión para introducir tests inseguros.** Advertencia de
  guardarraíl: sembrar specs de `core/guards/auth.guard.ts` y de los servicios HTTP de auth
  (`core/services/auth.service.ts`) NUNCA debe fijar/loggear credenciales reales ni tokens en
  los tests; usar dobles/fakes (patrón ya establecido en `auth.interceptor.spec.ts`). Los
  specs son código que gitleaks escanea: un secreto de prueba mal escrito rompería el gate.

## Positions

AGREE: El diseño "umbral dentro de `ng test`, heredado por `ci.yml` y `verify`" no debilita el gate; añade señal a un paso ya bloqueante.
AGREE: gitleaks permanece bloqueante en ambos caminos (@v3 en PR, @v2 en `verify`, sin `continue-on-error`); este intent no lo toca.
AGREE: El trinquete solo-sube pertenece a `## Forbidden` como restricción dura (prevención de relajar un control de calidad).
AGREE: `@vitest/coverage-v8` es el proveedor OSS de menor riesgo de cadena de suministro (mismo scope `@vitest` ya confiado) y de coste 0 €.
OBJECT: El borrador propone añadir `@vitest/coverage-v8` sin fijar política de pin; una herramienta que mide un gate bloqueante debe ir a versión exacta (o casada con `vitest` 4.x), no a rango abierto (G1).
OBJECT: Falta registrar como deuda de pipeline el diferimiento de SAST/DAST del frontend (G2), para no cerrarlo por omisión como sí se hizo explícito con la paridad `--cov` de backend.
OBJECT: Falta un guardarraíl explícito de que los specs sembrados de auth no fijen secretos/tokens reales (usar fakes), dado que gitleaks escanea también los `*.spec.ts` (G3).
