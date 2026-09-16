# NFR Requirements — u1-durable-session

> Construction (arquitecto, con perspectivas de seguridad/cumplimiento/calidad). Cuantifica
> los NFR de la sesión durable. Los NFR de inception ya están definidos; aquí se derivan
> targets `NFRx.y` medibles. Responde en el tag `[Answer]:`. `X. Other (please specify)`.

## Sources

- functional-design/functional-spec.md, rules.md (BR1.1–BR1.6) [scope]
- requirements.md (NFR1 seguridad, NFR2 rendimiento, NFR3 coste, NFR4 no-regresión, NFR5 multi-instancia) [scope]
- contract-summary.md (C1: sin plaintext, sin reintentos internos) [scope]
- codekb/technology-stack.md (FastAPI, Neon, db_connection sin ORM) [scope]
- team.md (coste 0€; pytest + fakes de persistencia) [scope]

---

## Q1 — Rendimiento del camino de sesión (NFR2)

`requirements.md` deja el umbral numérico de NFR2 para medición en build. ¿Cómo lo fijamos como
requisito comprobable ahora?

- A. **Sin umbral numérico bloqueante; presupuesto de latencia relativo**: NFR2.1 = "la persistencia
  de sesión no añade más de una lectura/escritura a BD por operación en el camino caliente; el caché
  en memoria sirve el hit sin ir a BD". Se valida por diseño + medición en build (no un p99 absoluto,
  coherente con NFR2 y coste 0€ sin infra de load-testing dedicada).
- B. **Umbral numérico absoluto** (p. ej. p95 < 200ms del camino de sesión) desde ya.

[Answer]: A

---

## Q2 — Seguridad de la credencial (NFR1) — perspectiva devsecops

¿Qué requisitos de seguridad `NFRx.y` fijamos para la credencial protegida?

- A. **Conjunto mínimo alineado con la regla dura y el guard existente**:
  - NFR1.1: la contraseña Futmondo nunca en claro en BD ni logs (verificable por escaneo/tests).
  - NFR1.2: el material de credencial solo accesible tras `CredentialProtection`; el secreto de
    protección (si el diseño cifra en reposo) vía secret de Fly.io, nunca literal en el repo.
  - NFR1.3: el arranque exige `JWT_SECRET` no-default (ya endurecido en `test_jwt_startup.py`).
  - NFR1.4: gitleaks bloqueante en CI cubre la no-introducción de secretos.
- B. Añadir/quitar algo (indícalo en Other).

[Answer]: A

---

## Q3 — Fiabilidad/durabilidad de la sesión (NFR5 + fiabilidad) — perspectiva calidad

- A. **NFR5.1 (durabilidad)**: la sesión persistida sobrevive a reinicio/redeploy (verificable por
  test de caracterización + test del nuevo contrato: reconstruir tras reinicio simulado con fake de
  persistencia). **NFR5.2 (multi-instancia)**: la lectura/escritura no asume instancia única; la
  autoridad es la BD. Sin SLA de disponibilidad numérico nuevo (el servicio ya tiene su healthcheck).
- B. Otra (indícalo en Other).

[Answer]: A

---

## Q4 — Observabilidad (perspectiva operaciones/calidad)

¿Qué observabilidad mínima exigimos para la sesión durable, a coste 0€?

- A. **Logging estructurado sin secretos**: log de eventos clave (rehidratación intentada, resultado
  active/unrecoverable, 401 accionable) SIN incluir la contraseña ni el material de credencial
  (refuerza NFR1). Sin nueva infra de métricas/tracing de pago; se apoya en los logs de Fly.io
  existentes. Métrica implícita: nº de 401 por sesión-no-reconstruible observable en logs.
- B. Añadir métricas/tracing dedicados (implicaría infra; chocar con coste 0€).

[Answer]: A

---

## Q5 — Decisiones de tech-stack (tech-stack-decisions.md)

¿Confirmas que la unidad NO introduce stack nuevo?

- A. **Sí, sin stack nuevo**: se reutiliza FastAPI + `db_connection` (Neon) + pytest + el patrón de
  fakes de persistencia; la única decisión abierta (cifrado en reposo vs. re-auth, FR5.2) se resuelve
  en NFR Design, y si elige cifrado usará una librería estándar de la stdlib/entorno sin dependencia
  de pago (coste 0€). Sin ORM nuevo, sin servicios nuevos.
- B. Se necesita alguna decisión de stack nueva (indícalo en Other).

[Answer]: A

---

## Consolidated Summary Confirmation

NFR derivados (`NFRx.y`) que se materializarán en los seis artefactos de nfr-requirements
más `traceability.json`:

**Performance (NFR2 → performance-requirements.md):**
- NFR2.1: la persistencia de sesión no añade más de una operación de BD por operación en el
  camino caliente; el caché en memoria sirve los hits sin ir a BD. Sin umbral numérico
  absoluto; validado por diseño + medición en build. [Q1-A]

**Security (NFR1 → security-requirements.md), perspectiva devsecops:**
- NFR1.1: contraseña Futmondo nunca en claro en BD ni logs (verificable por escaneo/tests).
- NFR1.2: material de credencial solo accesible tras CredentialProtection; secreto de
  protección (si cifra en reposo) vía secret de Fly.io, nunca literal en el repo.
- NFR1.3: arranque exige JWT_SECRET no-default (ya endurecido en test_jwt_startup.py).
- NFR1.4: gitleaks bloqueante en CI. [Q2-A]

**Reliability/durabilidad (NFR5 → reliability-requirements.md), perspectiva calidad:**
- NFR5.1: la sesión persistida sobrevive a reinicio/redeploy (test caracterización + nuevo
  contrato con fake de persistencia).
- NFR5.2: autoridad en BD, no asume instancia única. Sin SLA numérico nuevo. [Q3-A]

**Scalability (→ scalability-requirements.md):** sin objetivos de escalado nuevos; la unidad
tolera reinicio y escalado eventual vía autoridad en BD (NFR5.2); coste 0€ acota infra.

**Observability (→ observability-requirements.md), perspectiva operaciones:**
- NFR-OBS.1: logging estructurado de eventos de sesión (rehidratación intentada, resultado
  active/unrecoverable, 401 accionable) SIN secretos ni credencial (refuerza NFR1.1). Se apoya
  en los logs de Fly.io existentes; sin infra de métricas/tracing de pago. [Q4-A]

**Tech-stack (→ tech-stack-decisions.md):** sin stack nuevo — FastAPI + db_connection (Neon) +
pytest + fakes de persistencia. La elección cifrado-vs-re-auth (FR5.2) se resuelve en NFR Design
con librería estándar sin coste. [Q5-A]

**Coste (NFR3) y no-regresión (NFR4):** transversales; ninguna decisión NFR introduce coste
recurrente ni rompe la suite existente.

**Traceability:** NFR1→(NFR1.1..1.4), NFR2→NFR2.1, NFR5→(NFR5.1, NFR5.2); NFR3/NFR4 como N/A
justificados (transversales del intent, no específicos de la unidad).

[Answer]: Looks correct
