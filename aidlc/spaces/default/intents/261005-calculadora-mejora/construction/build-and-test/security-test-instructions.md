# Security Test Instructions — calculadora-mejora

## Estado

**NO-APLICA** una suite de seguridad dedicada en este intent. El cambio es
frontend-only, sin manejo de credenciales ni endpoints nuevos; no toca auth,
backend ni god-files. Estrategia Minimal, scope refactor.

## Controles de seguridad vigentes (sin cambios)

- `gitleaks` (bloqueante en CI) escanea también los `*.spec.ts`; el spec nuevo
  usa datos sintéticos, sin credenciales/tokens reales.
- `localStorage` solo guarda un booleano de preferencia (`futmondo_calc_include_onsale`);
  no es dato sensible.
- Sin SAST/DAST nuevo: no se introduce superficie de ataque.

## Sources

- `requirements.md`, `code-summary.md`.
- `aidlc-state.md` → `Test Strategy: Minimal`.

## Assumptions & Open Questions

None.
