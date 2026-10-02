# Security Test Instructions — `261001-sync-god-file-resto`

## Aplicabilidad

**No aplica** una suite de seguridad nueva en este intent (estrategia Minimal,
refactor de equivalencia estricta). No se introduce superficie de ataque nueva:
sin endpoints nuevos, sin entradas de usuario nuevas, sin dependencias nuevas.

## Controles existentes (perspectiva DevSecOps)

- **Secretos**: `gitleaks` bloqueante en CI escanea código y tests; los tests de
  este intent usan fakes en memoria, sin credenciales/tokens reales.
- **No-credenciales-en-logs**: la caracterización de `clauses` incluye un test
  que asevera que el mensaje de error no contiene material de credencial (FR6.3,
  BR4.2); comportamiento preservado verbatim del código original.
- **Dependencias**: sin dependencias nuevas; el audit de dependencias del gate
  (pip-audit/npm audit) sigue cubriendo la superficie existente.
