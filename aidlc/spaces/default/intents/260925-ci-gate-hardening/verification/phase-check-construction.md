# Phase Check — Construction → Operation (Intent 4: gate CI/CD hardening)

> Verificación de frontera Construction → Operation, **adaptada al scope infra**
> (config-only de CI/CD). Q4=A: no se fabrica traceability inexistente; se
> documenta qué se omitió por diseño del scope y se verifica lo que sí aplica.

## Contexto del scope

Scope **infra**, config-only. El scope omite por diseño las etapas de
**code-generation (3.5)** y **build-and-test (3.6)** — no se genera código de
aplicación nuevo ni se ejecuta una suite nueva de tests de aplicación. Por eso
`consumes_absent` marca `code-summary`, `build-and-test-summary` y
`test-results` como ausentes con `expected: true`.

En consecuencia, **no existen** los artefactos que el Step 5 estándar leería:
- `construction/build-and-test/cross-unit-traceability.md` — N/A (build-and-test omitido).
- `construction/*/code-generation/traceability.json` — N/A (code-generation omitido).

Estos no son gaps: son ausencias por diseño del scope. No se fabrican.

## Qué se verifica en su lugar

El "código" que este intent produce es **configuración de CI/CD y tooling
versionados** (workflows de GitHub Actions, `pytest.ini`, `angular.json`,
`requirements.txt`, allowlist + script). La verificación de frontera confirma:

| Verificación | Estado | Evidencia |
|--------------|--------|-----------|
| Cadena de diseño trazada NFR Requirements → NFR Design → Infrastructure Design → CI Pipeline | OK | `nfr-design/traceability.json` (21↔21 OK), `infrastructure-design/traceability.json` (16↔16 OK), este stage `ci-config.md` + `quality-gates.md` |
| Las quality gates de CI enforced coinciden con el diseño | OK | `quality-gates.md` mapea cada gate a su criterio pass/fail en ambos workflows |
| Gate base ya operativo pasa en verde (línea base) | OK (línea base en producción) | `ci.yml` job `quality` + `fly-deploy.yml` job `verify` con gitleaks + `pytest` + `ng test` bloqueantes; el sistema está en producción con este gate operativo |
| El intent ENDURECE (no relaja) la verificación existente | OK | Ratchet solo sube; promoción advisory→bloqueante escalonada; paridad PR↔push añadida; sin `continue-on-error` permanente |
| Cadena `needs:` de deploy intacta | OK | `verify → deploy-backend → deploy-frontend → smoke-test` sin reordenar (`ci-config.md` §Qué NO cambia) |
| Sin findings sin resolver en los artefactos de diseño | OK | Revisión adversarial de arquitectura READY en nfr-design (security-design) e infrastructure-design (cicd-pipeline); 2 sugerencias menores no bloqueantes cada una, trasladadas al gate |

## Veredicto

**PASS (adaptado a scope infra).**

- Code-generation y build-and-test omitidos por diseño del scope; no se fabrica
  traceability de aplicación inexistente.
- La cadena de diseño (NFR Requirements → NFR Design → Infrastructure Design →
  CI Pipeline) está trazada y las quality gates de CI reflejan el diseño.
- El gate de CI ya operativo es la línea base verde; este intent lo endurece de
  forma aditiva y escalonada, sin relajar garantías ni cambiar la topología de
  deploy.
- No quedan findings sin resolver que bloqueen la transición.

La materialización de los commits `chore(ci)` (medición del piso, pins exactos,
verificación en verde en ambos gates) es la ejecución posterior; el diseño y la
configuración accionable están completos y verificados en frontera.

## Sources

- `../ci-pipeline/ci-config.md`, `../ci-pipeline/quality-gates.md`.
- `../infrastructure-design/traceability.json`, `../nfr-design/traceability.json`.
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (adaptación coste 0 €).
