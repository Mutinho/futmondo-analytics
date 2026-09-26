# NFR Requirements — Preguntas (Intent 4, gate CI/CD hardening)

Run a nivel de workflow (scope infra; sin unit tag). functional-design y
units-generation están ausentes por diseño del scope (`consumes_absent`
expected); el contexto NFR se deriva de `requirements.md` y del codekb, sin
inventar artefactos ausentes.

Todas las decisiones NFR relevantes de este intent ya quedaron afirmadas en
practices-discovery (Q1–Q6) y fijadas en `requirements.md` (NFR1–NFR6):
coste 0 €, aislamiento por commit, no reformateo brownfield, secretos vía
`secrets`/JWT efímero, reproducibilidad del gate (auditar entorno instalado,
pins), idioma. Los únicos valores diferidos (piso backend, delta frontend) son
mediciones, no decisiones, y se resuelven en ci-pipeline.

**No hay preguntas abiertas genuinas para el humano en esta etapa.** Las
categorías NFR clásicas de runtime (latencia de usuario, throughput,
escalabilidad de usuarios concurrentes) **no aplican**: este intent es
config-only de CI/CD y no toca el runtime de la aplicación; se marcan N/A con
justificación en los artefactos. Las NFR que sí aplican son las del pipeline/gate
(reproducibilidad, fiabilidad del gate, seguridad de supply-chain, observabilidad
del CI, coste 0 €), ya derivadas de FR11–FR16 y NFR1–NFR6.

## Consolidated Summary Confirmation

Resumen de los artefactos NFR que se generarán (a nivel de gate CI/CD, no runtime):

- performance-requirements.md — N/A al runtime de la app; objetivo relevante = tiempo/coste del gate dentro del free tier (minutos de Actions), sin regresión de la duración del pipeline.
- security-requirements.md — supply-chain: pip-audit (findings con fix bloquean) / npm audit (high), allowlist versionada con caducidad, gitleaks unificado, secretos vía secrets/JWT efímero, pins exactos.
- scalability-requirements.md — N/A (no cambia la escalabilidad de la app); nota sobre volumen de findings/deuda heredada al promover.
- reliability-requirements.md — fiabilidad y reproducibilidad del gate: auditar entorno instalado (no rangos), pins de tooling, sin flapping (arreglar test, no bajar piso), rollback quirúrgico por commit aislado.
- observability-requirements.md — señal del gate: cobertura backend con piso visible en ambos gates (PR+verify), estado de audits/lint, smoke `/health` intacto; adaptado a Fly.io + GitHub Actions (sin servicios de pago).
- tech-stack-decisions.md — tooling OSS del gate fijado a versión exacta: ruff, pip-audit, vitest (emparejado con @vitest/coverage-v8==4.1.11), gitleaks unificado; coste 0 €.
- traceability.json — cobertura de NFR1–NFR6 de requirements.md a los NFRx.y derivados.

¿Todo correcto antes de generar los artefactos NFR?

[Answer]: Looks correct
