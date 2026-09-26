# Environment Provisioning — Preguntas (Intent 4: gate CI/CD hardening)

> Etapa de fase Operation. El conocimiento del stage asume aprovisionamiento
> AWS; se adapta al stack real (Fly.io + Neon, coste 0 €) y al carácter
> config-only del intent: **no se aprovisiona ni se cambia ningún entorno**. El
> entorno de producción (dos apps Fly.io `cdg` + Neon Frankfurt) ya existe y no
> cambia. Estas preguntas cierran el encuadre del inventario y la validación.

---

## Q1 — Alcance del aprovisionamiento en este intent

¿Qué provisiona esta etapa?

- A. **Ninguno nuevo — validación del entorno existente**: el intent es
  config-only de CI/CD; no crea ni modifica entornos. La etapa inventaría el
  entorno de producción existente (Fly.io + Neon) y valida que las expectativas
  del gate endurecido sobre el entorno (secretos, `JWT_SECRET` efímero en CI,
  `FLY_API_TOKEN`) se cumplen. Marcar NO-APLICA lo AWS-específico.
- B. Provisionar un entorno de staging nuevo.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Auditoría de secretos (perspectiva DevSecOps/Compliance)

¿Qué cubre la auditoría de secretos del entorno?

- A. **Inventario de secretos por ubicación, sin exponer valores**: `JWT_SECRET`
  (Fly secret productivo en `futmondo-api`; efímero no-productivo en CI),
  `DATABASE_URL` (Fly secret, Neon), `FLY_API_TOKEN` (GitHub Actions secret para
  deploy), `GITHUB_TOKEN` (gitleaks). Confirmar que ninguno está en claro en el
  repo (gitleaks bloqueante lo garantiza) y que el gate endurecido no introduce
  secretos nuevos. Referenciar por nombre, nunca por valor.
- B. Rotación de secretos como parte de este intent.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Mapeo de la red / seguridad de red (guardrail Operation)

El guardrail de Operation pide validar VPC/subnets/security groups/NACL. En
Fly.io esto no aplica en términos AWS. ¿Cómo se resuelve?

- A. **NO-APLICA (términos AWS) + documentar el equivalente gestionado**: Fly.io
  gestiona red/routing/TLS; no hay VPC/subnets/SG/NACL que validar. La
  conectividad a Neon es TLS gestionado. Documentar el equivalente gratuito y
  marcar NO-APLICA lo AWS, sin inventar topología de red inexistente. El intent
  no cambia red ni cifrado (sin risk assessment de infraestructura requerido).
- B. Diseñar/validar una topología de red tipo VPC.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Contenido de `validation-report.md`

¿Qué valida el informe?

- A. **Validación del entorno existente + de las expectativas del gate
  endurecido**: (i) las dos apps Fly.io responden a su healthcheck (`/health`,
  `/`); (ii) los secretos requeridos están presentes por ubicación (sin valores);
  (iii) el gate endurecido no requiere ningún recurso de entorno nuevo; (iv)
  paridad de secretos entre PR-gate y push-gate (ambos usan `GITHUB_TOKEN`
  efímero para gitleaks, `JWT_SECRET` efímero para pytest). Marcar NO-APLICA lo
  AWS (drift detection de Config, etc.) con su equivalente gratuito (diff de git
  sobre `fly.toml`/workflows).
- B. Un informe de validación de infraestructura AWS completo.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Health metric / error rate metric (guardrail Operation)

El guardrail pide que cada componente tenga al menos una métrica de salud y una
de error. ¿Cómo se satisface en este stack a coste 0 €?

- A. **Métricas existentes, sin componentes nuevos**: `futmondo-api` →
  healthcheck `/health` (salud) + rate de fallos del smoke test / no-200
  (error); `futmondo-app` → healthcheck `/` (salud). El gate (nuevo "componente"
  lógico) → pass/fail por paso en el log de Actions (salud) + tasa de rojos
  (error). Sin métricas de pago (CloudWatch); observables con `fly status` /
  `fly logs` / el log de Actions. El intent no añade servicios que requieran
  métricas nuevas.
- B. Instrumentar métricas nuevas con un servicio dedicado.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de Environment Provisioning (config-only; entorno de
produccion existente sin cambios; AWS adaptado a Fly.io/Neon coste 0 EUR):

- **Q1 — Alcance (A)**: ninguno nuevo; inventariar el entorno existente (dos apps
  Fly.io + Neon) y validar las expectativas del gate endurecido. NO-APLICA lo
  AWS-especifico.
- **Q2 — Secretos (A)**: inventario por ubicacion sin exponer valores
  (`JWT_SECRET`, `DATABASE_URL`, `FLY_API_TOKEN`, `GITHUB_TOKEN`); nada en claro
  (gitleaks bloqueante); el gate no introduce secretos nuevos.
- **Q3 — Red (A)**: NO-APLICA en terminos AWS (Fly gestiona red/routing/TLS; Neon
  TLS); documentar el equivalente gestionado; sin cambios de red/cifrado.
- **Q4 — `validation-report.md` (A)**: validar healthchecks (`/health`, `/`),
  secretos presentes por ubicacion, ausencia de recursos nuevos, paridad de
  secretos PR<->push; NO-APLICA drift AWS con equivalente (diff de git).
- **Q5 — Metricas salud/error (A)**: metricas existentes (`/health`, `/`,
  pass/fail de Actions); sin servicios de pago nuevos.

Se generaran: `environment-inventory.md` y `validation-report.md`, respetando el
mandato coste 0 EUR, la adaptacion Fly.io/Neon y todas las reglas afirmadas.

[Answer]: Looks correct
