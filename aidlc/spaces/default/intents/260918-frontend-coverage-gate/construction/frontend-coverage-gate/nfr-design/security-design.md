# Diseño de Seguridad (NFR Design) — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). Diseño técnico de **cómo** se realizan los requisitos de seguridad afirmados en `security-requirements.md` (NFR1.1–1.5). No hay servicio desplegable ni datos en reposo nuevos; el diseño de seguridad es de cadena de suministro, no-filtración de secretos e integridad del gate de CI. No es código (eso es code-generation); son decisiones de diseño con snippets ilustrativos ≤15 líneas.

## Diseño por requisito

### NFR1.1 — Cadena de suministro del proveedor de cobertura (pin exacto)

- Se añade `@vitest/coverage-v8` a `devDependencies` de `angular-app/package.json` con **versión exacta** (sin `^`/`~`), casada en major con `vitest` `^4.0.x` ya presente. `package-lock.json` se regenera con `npm install` y se commitea.
- Snippet ilustrativo (diseño, no implementación final):
  ```jsonc
  // angular-app/package.json (devDependencies) — versión exacta a fijar en implementación
  "@vitest/coverage-v8": "4.0.8"   // debe casar el major.minor de vitest instalado
  ```
- Verificación de diseño: el major/minor del proveedor coincide con el de `vitest`; un mismatch de major rompe la instrumentación (ver tech-stack-decisions TS1).

### NFR1.2 — Verificación reproducible antes de pushear

- Diseño del procedimiento: ejecutar `npm ci` + `ng test` en contenedor `node:22.22.3` (volumen anónimo para `node_modules`) antes de pushear el cambio de devDependencies. `npm audit` (advisory) corre en CI sobre el lockfile actualizado.
- No es un control en runtime; es un guardarraíl de proceso (regla dura Q7-B) que evita romper el gate de CI.

### NFR1.3 — No-filtración de secretos en specs

- Diseño de los specs sembrados de auth: usan dobles/fakes exclusivamente.
  ```ts
  // Patrón de diseño (auth.service.spec.ts) — sin secretos reales
  const httpMock = TestBed.inject(HttpTestingController);
  // token de prueba inventado, nunca un JWT real:
  const fakeToken = 'test.fake.jwt';
  ```
- gitleaks (bloqueante, `@v3` en PR / `@v2` en `verify`) escanea también los `*.spec.ts`; el diseño garantiza que ningún literal parezca un secreto real.

### NFR1.4 / NFR1.5 — Integridad del gate al añadir el umbral

- Diseño del cableado: el umbral de cobertura se declara en el target `test` de `angular.json` (fuente única) y `ng test` lo ejerce. El paso `ng test` **sigue bloqueante** en `ci.yml` (PR) y en `verify` (push→`main`); no se convierte ningún paso bloqueante (gitleaks, pytest, ng test) en advisory.
- Cualquier paso adicional de reporte de cobertura (p. ej. subir un resumen) es **solo observabilidad** y no lleva `continue-on-error` que sustituya el enforcement dentro de `ng test`.
- Diseño del ratchet: el umbral solo sube (revisión manual por MR); nunca se baja para pasar el gate (regla dura Q7-A). El diseño no incluye ningún mecanismo automático que reescriba el umbral a la baja.

## Categorías NFR no aplicables (kind packaging)

- Resiliencia/circuit-breakers/caching, escalabilidad, observabilidad de servicio (SLI/SLO), disaster recovery: **N/A** — no hay servicio en runtime que diseñar. La "observabilidad" relevante es el reporte de cobertura de CI, ya cubierto como observabilidad no bloqueante.

## Deuda de seguridad diferida

- SAST/DAST del frontend: fuera de alcance (Q8=A); registrado como deuda de pipeline.

## Assumptions & Open Questions

- La sintaxis exacta de las opciones de cobertura del builder `@angular/build:unit-test` de Angular 22 (dónde declarar `coverage.provider`/`thresholds` en el target `test`) se valida en el spike de cableado de code-generation (supuesto A2).
