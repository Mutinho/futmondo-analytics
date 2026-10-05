# Security Test Instructions — Minimal / refactor (sin árbol nuevo; invariantes verificados)

## Decisión

El scope es **refactor** → estrategia **Minimal**: no se genera árbol SAST/DAST
nuevo. La seguridad relevante a este refactor es la **invariante de credenciales
(NFR6)**, que se verifica estáticamente sobre el código generado y por el gate
de secretos ya operativo.

## Invariantes verificados (perspectiva security engineer)

- **NFR6 — sin credenciales/tokens en claro**: ninguna extracción introduce
  password ni token Futmondo en claro, ni en mensajes, `repr` o `exc_info`. El
  manejo de errores legacy se movió **verbatim** (no se añadió logging de
  material sensible). Verificación: inspección del árbol nuevo
  `backend/app/services/data_manager/**` + los 14 tests nuevos; `gitleaks` es
  **bloqueante** en el gate de CI (PR) y en el job `verify` (push) y escanea
  también los tests (que usan sólo fakes/literales, sin credenciales reales).
- **Inyección (OWASP A03)**: el SQL se mueve **verbatim** y sigue
  **parametrizado** (placeholders `?`/`%s` existentes); no se construye SQL por
  concatenación de input de usuario en la extracción. Sin cambio de superficie
  de inyección.
- **Superficie de ataque sin cambios**: los routers consumidores y su
  autenticación/autorización **no se tocan** (BR4.1); la frontera pública es
  idéntica (57 métodos byte a byte).

## Qué se ejecuta

- `gitleaks` (gate CI/verify) — detección de secretos, bloqueante. Sin cambio de
  config en este intent.
- La suite `backend/tests/` corre sin red/BD/credenciales reales (NFR6),
  confirmado verde (ver `test-results.md`).

## Owning stage

No hay SAST/DAST diferido con owner en este scope. El escaneo de secretos vive
permanentemente en el pipeline (`ci.yml` + `fly-deploy.yml verify`).
