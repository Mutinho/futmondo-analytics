# Quality Gates — F2

> Fase: construcción (ci-pipeline). Idioma: castellano; tokens técnicos verbatim en inglés.

## Gate de CI (existente, sin cambios)

El PR de F2 pasa por el gate bloqueante ya operativo; **ningún umbral se modifica** (invariante del trinquete: sólo sube):

| Check | Estado en F2 |
|-------|--------------|
| gitleaks | corre (escanea Swift nuevo); debe quedar limpio |
| `ruff check` / `pytest` / `pip-audit` | sin impacto (backend no cambia) |
| `ng test` (cobertura 19/19/17/18) | sin impacto (frontend Angular no cambia) |
| `npm audit --audit-level=high` | sin impacto |

## Gate local del código iOS (manual, deuda aceptada)

- `cd ios && swift build && swift test` verde (87 tests) antes de pushear — responsabilidad del desarrollador; no hay runner Swift en el CI (follow-up).
- Validación de UI en iPhone 13 Pro.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/ci-pipeline/ci-config.md`
- `aidlc/spaces/default/memory/team.md`

## Assumptions & Open Questions

None.
