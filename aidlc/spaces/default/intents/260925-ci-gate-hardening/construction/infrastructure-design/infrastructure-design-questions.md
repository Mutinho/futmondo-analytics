# Infrastructure Design — Preguntas (Intent 4: gate CI/CD hardening)

> Etapa de diseño de infraestructura. La "infraestructura" de este intent
> config-only es: los workflows de GitHub Actions (`ci.yml`, `fly-deploy.yml`),
> la topología Fly.io/Neon (SIN cambios) y la estructura del gate. Lo ya
> afirmado NO se re-pregunta: dos apps Fly.io (`cdg`), Neon free, cadena
> `needs:` intacta, deploy on-merge, smoke test `/health`, secretos vía
> `secrets`, coste 0 €. Estas preguntas resuelven las decisiones de
> **infraestructura del pipeline** que quedan abiertas.

---

## Q1 — Orden de los pasos dentro del job (audits/lint/cobertura vs tests)

Dentro de cada job del gate, ¿en qué orden se colocan los nuevos pasos
bloqueantes respecto a la suite de tests, para optimizar el feedback y el coste
de minutos?

- A. **Barato-y-rápido primero (fail-fast)**: gitleaks → allowlist expiry check
  → `pip-audit`/`npm audit` → `ruff check` → `pytest --cov`/`ng test`. Los pasos
  de segundos fallan antes de gastar minutos en la suite completa.
- B. **Tests primero** (mantener el orden actual y añadir audits/lint al final).
- C. Sin orden prescrito (cada paso independiente, orden indiferente).
- X. Other (please specify)

[Answer]: A

---

## Q2 — Ubicación del allowlist expiry check (reutilizable en ambos gates)

El chequeo determinista de caducidad de la allowlist (decidido en NFR Design)
corre en ambos gates (PR y push). ¿Cómo se materializa para no duplicar lógica?

- A. **Script versionado único en el repo** (p. ej. `scripts/check-allowlist-expiry.sh`
  o `.py`), invocado como un `run:` step con nombre propio en ambos workflows —
  una sola fuente de verdad, sin composite action nueva.
- B. **Composite action local** (`.github/actions/allowlist-expiry/`) reutilizada
  por ambos jobs.
- C. **Inline en cada workflow** (script embebido en el YAML, duplicado).
- X. Other (please specify)

[Answer]: A

---

## Q3 — Estrategia frente a los minutos de GitHub Actions (NFR1.1)

Medir cobertura backend en dos jobs (PR + push) es el coste marginal dominante.
¿Qué estrategia de infraestructura se diseña para el free tier?

- A. **Documentar el consumo y fijar umbral de alerta manual** (FR16): estimar
  minutos/mes, identificar el punto que forzaría salir del free tier, y dejar la
  paridad de cobertura en ambos jobs como coste aceptado. Sin optimización
  prematura.
- B. **Optimizar ya**: p. ej. condicionar la medición de cobertura en `verify`
  (push) a ciertos paths o saltarla si el PR ya la midió.
- C. **Cache agresivo** como única palanca documentada.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Alcance del artefacto `cicd-pipeline.md` (el que revisa arquitectura)

Este intent endurece un pipeline existente maduro. ¿Qué alcance tiene
`cicd-pipeline.md`?

- A. **Diseño del pipeline endurecido como delta sobre el existente**: documentar
  el mapeo etapa→gate resultante (ambos workflows), los pasos añadidos/promovidos,
  el orden (Q1), la ubicación del expiry check (Q2), secrets management en CI, y
  la secuencia de commits `chore(ci)` escalonados; marcando explícitamente qué NO
  cambia (topología, cadena `needs:`, deploy, crons).
- B. **Documentar el pipeline completo desde cero** (incluyendo lo que no cambia
  en detalle).
- X. Other (please specify)

[Answer]: A

---

## Q5 — Monitoring del gate en `monitoring-design.md` (coste 0 €)

Sin CloudWatch/SLO de pago. ¿Cómo se enfoca `monitoring-design.md` para este
intent?

- A. **Monitoreo de la señal del gate con herramientas gratuitas**: pasos con
  nombre en el log de Actions como métricas de pass/fail, `fly logs` + `/health`
  como observabilidad de runtime existente, allowlist auditable en git, y
  minutos de Actions como métrica de coste; marcando NO-APLICA/diferido lo de
  pago (SLO con burn-rate, tracing distribuido, anomaly detection ML).
- B. **Inventario mínimo** que remita a lo existente sin detalle.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de infraestructura del pipeline:

- **Q1 — Orden de pasos (A)**: fail-fast — barato-y-rápido primero (gitleaks →
  expiry check → audits → lint → tests/cobertura).
- **Q2 — Expiry check (A)**: script versionado único en el repo, invocado como
  `run:` step con nombre propio en ambos gates.
- **Q3 — Minutos de Actions (A)**: documentar el consumo y el umbral de free tier
  (FR16), aceptando la paridad de cobertura como coste necesario.
- **Q4 — `cicd-pipeline.md` (A)**: diseño del pipeline endurecido como DELTA
  sobre el existente, marcando qué NO cambia (topología, cadena `needs:`, deploy,
  crons).
- **Q5 — `monitoring-design.md` (A)**: monitoreo del gate con herramientas
  gratuitas, marcando NO-APLICA/diferido lo de pago.

Se generarán 4 artefactos: `infrastructure-specification.md`,
`monitoring-design.md`, `cicd-pipeline.md` y `traceability.json`, respetando el
mandato coste 0 €, la adaptación Fly.io/GitHub Actions y todas las reglas
afirmadas.

[Answer]: Looks correct
