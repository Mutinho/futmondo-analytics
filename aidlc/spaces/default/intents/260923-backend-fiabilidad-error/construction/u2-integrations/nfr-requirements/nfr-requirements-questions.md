# NFR Requirements — Preguntas · u2-integrations (Integraciones)

Fase Construction, profundidad Standard. Muchos NFR ya están fijados en
`requirements.md` (NFR1 observabilidad/logging, NFR2 no-corrupción, NFR3 sin
credenciales, NFR4 sin regresión, NFR5 coste 0 €) y en las prácticas afirmadas.
Además, este es un intent de **fiabilidad sobre stack existente** (FastAPI +
Neon + Fly.io, coste 0 €): performance/escalabilidad/topología **no cambian**.
Estas preguntas sólo cierran los huecos cuantificables genuinos de U2.

Aportan perspectiva (inline): seguridad (DevSecOps), calidad (QA) y cumplimiento
(Compliance).

---

## Q1 — Formato y nivel de log por modo de fallo (NFR1 → observabilidad)

NFR1 exige log estructurado con `sync_step`, `reason`, `failure_mode`, `status?`,
`endpoint?`, `task_id`, sin credenciales. Para `fly logs` + `grep` a coste 0 €:

- A. Log estructurado **clave=valor en una línea** (p. ej. `sync_step=sofascore
  failure_mode=ban status=403 task_id=... reason=...`), nivel **WARNING** para
  recuperable/`DEGRADED` y **ERROR** para fatal; sin dependencia nueva (logging
  stdlib). Grep-able con el patrón de campos existente.
- B. Log estructurado **JSON por línea** (un objeto JSON por evento), mismos
  niveles; más parseable por herramientas pero menos legible a ojo en `fly logs`.
- C. Reusar exactamente el patrón de logging ya presente en el código
  (`sync_step_status.py` / `sofascore_client.py`) sin fijar formato aquí.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Timeout de las llamadas de integración (performance/reliability)

Hoy Sofascore tiene throttle preventivo (~750 ms) y `requests` (Futmondo) puede
colgar. ¿Fijamos un presupuesto de timeout como requisito de fiabilidad para que
un proveedor lento no bloquee el sync indefinidamente?

- A. Sí: fijar un **timeout explícito por petición** en ambos clientes (valor
  concreto a decidir en nfr-design / code-generation, p. ej. connect+read
  acotados) y clasificar el timeout como recuperable (`IntegrationTimeoutError`,
  ya modelado). El requisito NFR se expresa como "toda llamada de integración
  tiene timeout acotado; sin timeout ilimitado".
- B. No fijar timeout en este intent (fuera de alcance, igual que retry/backoff);
  sólo tipar y clasificar el fallo cuando ocurra. Queda como deuda.
- X. Other (please specify)

[Answer]: A

---

## Q3 — SLO/SLI y disponibilidad para U2 (reliability)

El sync corre por crons Fly one-shot (04:30 / 05:00 UTC) y bajo demanda; no es un
endpoint interactivo con SLA. ¿Cómo expresamos el objetivo de fiabilidad de U2?

- A. **SLI informal, sin SLA formal** (coherente con el mandato coste 0 € y la
  guía de adaptación Fly.io): SLI = ausencia de pasos `DEGRADED` inesperados +
  no-corrupción de datos verificada por spec; sin burn-rate ni objetivo de
  disponibilidad porcentual (los cron toleran un fallo puntual: reintento en la
  siguiente ejecución programada). SLO formal con burn-rate → NO-APLICA/diferido.
- B. Fijar un objetivo de disponibilidad porcentual formal (p. ej. 99.x %) para
  la ruta de sync.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Alcance de amenazas de seguridad para U2 (security, STRIDE acotado)

U2 no cambia auth/authz (JWT, HttpOnly cookie ya existen) ni expone API pública
nueva; su superficie de seguridad relevante es el manejo de credenciales del
usuario hacia Futmondo y los datos que salen en logs/excepciones. ¿Acotamos así
los requisitos de seguridad?

- A. Sí: requisitos de seguridad de U2 = **Information Disclosure** (NFR3: nunca
  password/token en excepción, `repr`, `exc_info` ni log) + **Tampering/no-
  corrupción** (NFR2, ya cubierto en functional-design) + mantener el trato de
  secretos vía `fly secrets`/GitHub secrets. Auth/authz, rate-limiting de API,
  cifrado en tránsito a Neon → **sin cambios** (heredados), documentados como
  "sin cambio en este intent".
- B. Ampliar el modelado de amenazas de U2 más allá de eso (p. ej. revisar todo
  el borde HTTP), aunque no esté en el alcance del intent.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
