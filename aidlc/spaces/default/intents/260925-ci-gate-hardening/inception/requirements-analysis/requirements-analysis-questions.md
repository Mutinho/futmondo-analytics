# Requirements Analysis — Preguntas (Intent 4, gate CI/CD hardening)

Intent muy acotado (scope infra). El alcance funcional viene del plan de
análisis `260911-analisis-mejoras` (FR11, FR12, FR17.3, FR16 + deuda diferida
de pipeline) y las seis decisiones de diseño ya quedaron afirmadas en
practices-discovery (Q1–Q6). No se re-preguntan áreas ya decididas: alcance de
ESLint (diferido), severidad de audits (npm high / pip-audit findings-con-fix),
allowlist versionada con caducidad, paridad de audit/lint+cobertura en `verify`,
deuda de tooling a cerrar (gitleaks/ruff/pip-audit/vitest, auditar entorno
instalado), y granularidad del piso backend (line-only, valor exacto).

Solo queda una decisión de priorización de negocio:

## Q1 — FR16 (documentación de consumo de free tier): ¿alcance o anexo?

FR16 pide documentar el consumo actual dentro de los tiers gratuitos (minutos de
GitHub Actions, Neon free, Fly.io free allowance) e identificar los umbrales que
forzarían salir del free tier — sobre todo por el coste añadido de medir
cobertura y correr audits/lint en dos jobs (PR + `verify`). El plan lo marca
como **opcional**.

- A. Incluir FR16 como requisito NO funcional de este intent (documentación
  entregable), dado que el endurecimiento del gate añade minutos de Actions y es
  el momento natural de cuantificar el margen de free tier. (Recomendación.)
- B. Dejar FR16 fuera de alcance (deuda de documentación independiente); este
  intent solo endurece el gate y no entrega el doc de free tier.
- X. Other (please specify)

[Answer]: A. Incluir FR16 como requisito no funcional de documentación entregable de este intent (cuantificar el consumo y el margen de free tier).

## Consolidated Summary Confirmation

Resumen de los requisitos que se generarán en `requirements.md`:

- FR11 — Piso de cobertura backend bloqueante (`--cov-fail-under` en pytest.ini, line-only, valor medido exacto, ratchet solo-sube).
- FR12 — Promoción escalonada advisory→bloqueante: audits (pip-audit/npm audit) primero, luego `ruff check` backend; ESLint frontend fuera de alcance (deuda). npm audit en `high`, pip-audit bloquea findings con fix; findings sin fix → allowlist versionada con caducidad.
- FR13 — Deuda de tooling a cerrar: unificar/fijar gitleaks en ambos gates, pinnar ruff/pip-audit/vitest, auditar entorno instalado (no `-r`).
- FR14 (FR17.3) — Paridad real de gate PR↔push: añadir a `verify` cobertura+piso y los pasos audit/lint bloqueantes; no reordenar la cadena `needs:`.
- FR15 — Ratchet de cobertura frontend: subir umbrales de angular.json (fuente única); no tocar devDependencies.
- FR16 — Documentación de consumo/umbrales de free tier (entregable).
- NFR (coste 0 €, aislamiento por commit chore(ci), no reformateo brownfield, secretos vía secrets/JWT efímero, tests con fakes).
- Fuera de alcance: ESLint frontend, pin de acciones por SHA (ci-pipeline), branch-coverage backend, refactor de god-files/routers.

¿Todo correcto antes de generar `requirements.md`?

[Answer]: Looks correct
