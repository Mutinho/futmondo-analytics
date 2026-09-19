# Requisitos de Seguridad (NFR) — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). Requisitos de seguridad derivados de los NFR de inception (`requirements.md`) aplicables a esta intervención de tooling/pipeline. No hay lógica de negocio ni datos persistentes nuevos; la seguridad relevante es de cadena de suministro (nueva devDependency), integridad del gate y no filtración de secretos en specs.

## Requisitos

| ID | Requisito | Origen | Severidad |
|----|-----------|--------|-----------|
| NFR1.1 | El proveedor de cobertura `@vitest/coverage-v8` se añade como devDependency **a versión exacta (pin)**, casado en major con `vitest` 4.x; nada de rangos abiertos en un gate bloqueante. Es un paquete OSS de npm bien conocido (mismo scope `@vitest`), sin coste recurrente. | NFR1 (coste 0 €, cadena de suministro), regla dura Q7-D | Alta |
| NFR1.2 | Tras cambiar `package.json`/`package-lock.json`, verificar `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear; `npm audit` (advisory) se ejecuta en CI sobre el lockfile actualizado. | NFR5, regla dura Q7-B | Alta |
| NFR1.3 | Los specs de auth sembrados (`auth.guard`, `auth.service`, `auth.interceptor`) usan fakes/dobles (`vi.fn()`, `provideHttpClientTesting`), **nunca** secretos ni tokens reales; gitleaks escanea también los `*.spec.ts` en ambos caminos de CI. | Regla dura Q7-C, guardarraíl devsecops | Alta |
| NFR1.4 | La introducción del umbral de cobertura en `ng test` **no debilita** el gate de CI existente: gitleaks + pytest + ng test siguen BLOQUEANTES en PR (`ci.yml`) y en `verify` (`fly-deploy.yml`); no se convierte ningún paso bloqueante en advisory. | Mandato afirmado (gate bloqueante), FR17.1.2 | Alta |
| NFR1.5 | Cualquier paso adicional de reporte de cobertura es **solo observabilidad** y nunca lleva `continue-on-error` que sustituya al enforcement dentro de `ng test`. | FR17.1.2, guardarraíl devsecops | Media |

## Amenazas consideradas (STRIDE, acotado a la intervención)

- **Tampering / Supply-chain (T)**: una devDependency con rango abierto o typosquat podría inyectar código en el runner de CI. Mitigación: pin exacto de un paquete OSS del scope oficial `@vitest`, `npm audit` advisory, verificación en contenedor Node fijado (NFR1.1, NFR1.2).
- **Information disclosure (I)**: un token/secreto real hardcodeado en un spec podría filtrarse al historial. Mitigación: fakes/dobles obligatorios y gitleaks bloqueante sobre `*.spec.ts` (NFR1.3).
- **Elevation / Gate bypass (E)**: relajar el gate para pasar. Mitigación: gate bloqueante intacto, ratcheting solo-arriba (regla dura Q7-A), sin `continue-on-error` sustitutivo (NFR1.4, NFR1.5).

## Deuda de seguridad diferida (fuera de alcance, Q8=A)

- **SAST/DAST del frontend**: no hay análisis estático de seguridad más allá de ESLint advisory. Diferido a un futuro diseño de pipeline; registrado como deuda, no cerrado por omisión.

## Assumptions & Open Questions

- None.
