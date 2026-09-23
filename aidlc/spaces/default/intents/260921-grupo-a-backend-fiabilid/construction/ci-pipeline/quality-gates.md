# Quality Gates — Fiabilidad de la sync

> Conversation language: Spanish. Los gates ya están operativos en la CI del
> proyecto; esta etapa los documenta y verifica que ejercen los comandos que
> Build and Test registró. Modo escalonado (advisory → bloqueante).

## Gates bloqueantes (un rojo NO se fusiona ni despliega)

| Gate | Comando | PR (`quality`) | push→`main` (`verify`) | Requisito |
|---|---|---|---|---|
| Backend tests | `pytest tests` (con `--cov=app` en PR) | Sí | Sí | FR8.1, NFR3 |
| Frontend tests | `ng test --watch=false` (Vitest + cobertura por métrica) | Sí | Sí | FR17.1 |
| Escaneo de secretos | `gitleaks-action` (`@v3` PR / `@v2` verify) | Sí | Sí | FR5 |

- El enforcement de cobertura del frontend vive **dentro** de `ng test` (umbral
  por métrica en `angular.json`); si cae por debajo, el builder sale ≠ 0 y el job
  falla. Sin pasos extra ni `continue-on-error` que sustituyan al enforcement.
- El umbral de cobertura es **trinquete manual** (solo sube; nunca se baja para
  pasar el gate).

## Gates advisory (informan, no bloquean)

| Gate | Comando | Nota |
|---|---|---|
| Ruff lint (backend) | `ruff check .` | `continue-on-error: true` |
| ESLint (frontend) | `ng lint` | advisory |
| pip-audit (backend) | `pip-audit -r requirements.txt` | advisory |
| npm audit (frontend) | `npm audit --audit-level=high` | advisory |

## Enforcement de los comandos de Build and Test

Build and Test registró como comando de verdad de la unidad:
`python -m pytest tests` (backend). Ese comando es exactamente el que ejercen
los gates bloqueantes en **ambos** caminos de CI (`quality` y `verify`), de modo
que los 166 tests —incluidos los 4 nuevos de `sync-reliability`— corren en cada
PR y en cada push a `main`. El gate de calidad de la etapa Build and Test queda,
por tanto, cableado en CI sin cambios adicionales.

## Este intent

- **No añade ni relaja gates.** Backend-only y aditivo; los tests nuevos se
  incorporan al gate `pytest tests` existente. Se respeta el mandato: nunca
  bajar un umbral para pasar el gate.

## Sources

- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`,
  `construction/build-and-test/build-and-test-summary.md` (comandos de test),
  `team.md`/`project.md` (gates bloqueantes afirmados).

## Assumptions & Open Questions

None.
