# Security Test Instructions — frontend-coverage-gate

Estrategia **standard**. Este intent no añade superficie de ataque nueva; sus consideraciones de seguridad son de **higiene de tests** y **supply-chain del proveedor de cobertura**. El SAST/DAST del frontend está **fuera de alcance** (deuda de pipeline diferida, Q8=A).

## Controles verificables en esta suite

- **Sin secretos reales en specs (NFR4 / regla dura Q7-C)**: los specs de auth usan fakes/dobles (`fake-access-token-*`), nunca tokens/credenciales reales. `gitleaks` escanea también `*.spec.ts` en CI (bloqueante `@v3` en PR, `@v2` en `verify`).
  - Verificación: `grep -RIn "eyJ\|BEGIN .*PRIVATE KEY\|password\s*=\s*[\"']" angular-app/src/app/**/*.spec.ts` no devuelve secretos reales; el escaneo real lo hace `gitleaks` en el pipeline.
- **Invariante de seguridad congelada (NFR1.3/BR4.3)**: `auth.service.spec.ts` verifica que el access token vive en memoria y NUNCA se persiste en `localStorage`.
- **Supply-chain del proveedor (C3/NFR1)**: `@vitest/coverage-v8` es OSS (coste 0 €), fijado a versión exacta `4.1.11` (sin rangos abiertos en un gate bloqueante), casado en major con `vitest 4.1.11` (verificado en `package-lock.json`).

## Cómo ejecutar

Los controles de higiene se ejercen dentro de la suite unit y del escaneo de secretos del pipeline:

```bash
# suite (incluye la invariante token-en-memoria):
npx ng test --watch=false
# escaneo de secretos: gitleaks (ejecutado por CI en ci.yml y fly-deploy.yml verify)
```

## Diferido (fuera de alcance)

- **SAST/DAST del frontend**: no hay análisis estático de seguridad más allá de ESLint advisory; se difiere a un futuro diseño de pipeline (deuda registrada).
