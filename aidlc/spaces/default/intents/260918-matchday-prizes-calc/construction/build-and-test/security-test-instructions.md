# Security Test Instructions — matchday-prizes-calc

Superficie de seguridad del intent: **nula/mínima**. El cálculo de premios no
maneja secretos, no expone endpoints nuevos, no procesa PII nueva y no añade
dependencias.

- **Escaneo de secretos (gitleaks)**: bloqueante en el gate de CI (PR→`main`) y
  en el job `verify` (push→`main`). No se introdujeron secretos (único literal es
  el `JWT_SECRET` de arranque efímero de test, no productivo).
- **Ruff** sobre archivos nuevos: limpio. (Familia `S`/bandit se considera por
  trinquete futuro al endurecer ruff; fuera de alcance.)
- **STRIDE acotado**: el único riesgo de integridad es el borrado defensivo
  `DELETE ... NOT IN` sobre `team_prizes`, ya cubierto por la caracterización.
- Constraints de seguridad de línea base intactos (password no en claro,
  `JWT_SECRET` no-default): este intent no los toca.
