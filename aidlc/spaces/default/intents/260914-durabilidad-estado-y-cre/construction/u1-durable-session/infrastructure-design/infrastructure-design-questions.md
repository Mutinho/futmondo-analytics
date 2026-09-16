# Infrastructure Design — Preguntas (u1-durable-session)

> Etapa Infrastructure Design (Construction). Traigo la perspectiva de plataforma (Fly.io + Neon,
> aquí NO hay AWS) con apoyo de seguridad (devsecops) y cumplimiento (compliance). El sistema YA
> está en producción con pipeline maduro; esto es un mapeo acotado, no infra nueva. Restricción
> dura: coste 0€, sin servicios nuevos.
>
> Responde con `[Answer]: <letra>` (o `X` con tu texto). Deja en blanco lo que quieras que resuelva
> con el valor recomendado; si dejas alguna en blanco te lo marco antes de generar.

---

## Q1 — Cómo se crean las tablas nuevas en Neon (UserSession, ProtectedCredential)

La unidad añade 2 tablas a la BD Neon ya provisionada. Hoy el repo dispersa SQL crudo sin
migraciones formales.

- **A. Script SQL idempotente versionado en el repo (`CREATE TABLE IF NOT EXISTS ...`), aplicado
  en el arranque del backend o como paso previo del deploy (recomendada).** Sin herramienta de
  migraciones nueva (coste 0€, sin dependencia). Idempotente: seguro re-ejecutar. Encaja con el
  estilo actual y con "sin ampliar god-files".
- **B. Introducir una herramienta de migraciones (Alembic).** Más robusto a largo plazo, pero
  añade dependencia y andamiaje nuevo — sobre-ingeniería para 2 tablas en una intervención acotada.
- **X. Otra (especifica).**

[Answer]: A

---

## Q2 — Provisión y rotación del secreto `FUTMONDO_CRED_KEY` (clave de cifrado del handle)

El diseño de seguridad cifra el handle de re-auth con una clave gestionada como secret de Fly.io.

- **A. `fly secrets set FUTMONDO_CRED_KEY=...` por app (`futmondo-api`), fuera del repo; rotación
  manual documentada en runbook, con `scheme` versionado para re-cifrado perezoso en el siguiente
  login (recomendada).** Igual patrón que `JWT_SECRET`/`DATABASE_URL` actuales. Coste 0€. Sin
  rotación automática (innecesaria para el volumen y el TTL 12h del handle).
- **B. Rotación automática programada (cron/gestor de secretos).** Implica andamiaje o servicio
  nuevo; coste y complejidad no justificados aquí.
- **X. Otra (especifica).**

[Answer]: A

---

## Q3 — El gate de CI del push directo a `main` (`verify` de `fly-deploy.yml`) y gitleaks

`team.md` registra un hueco conocido: el job `verify` (push→`main`) corre `pytest -q` **sin
gitleaks** y sin `--cov`, mientras el gate de MR sí trae gitleaks (bloqueante). Relevante a FR5
(un secreto colado por push directo a `main` solo lo pararía el gate de MR).

- **A. Añadir gitleaks (bloqueante) al job `verify` de `fly-deploy.yml`, igualándolo al gate de MR
  para el escaneo de secretos (recomendada).** Defensa en profundidad coherente con FR5/NFR1.4;
  coste 0€ (acción de GitHub gratuita). El resto del gap (cobertura) se deja como está.
- **B. Dejar `verify` como está y apoyarse solo en branch protection (MRs obligatorios).** Menos
  robusto ante un push directo; mantiene el hueco que team.md ya señaló.
- **X. Otra (especifica).**

[Answer]: A

---

## Q4 — Estrategia de despliegue de esta unidad (sin cambios de topología)

La unidad no añade apps ni servicios; toca el backend `futmondo-api` (código + 2 tablas).

- **A. Reutilizar el pipeline actual sin cambios de estrategia: on-merge a `main` → `verify` →
  `deploy-backend` → `deploy-frontend` → `smoke-test` contra `/health` (recomendada).** La
  migración SQL idempotente (Q1) corre antes de/al arrancar el backend. Rollback = redeploy de la
  release anterior (runbook existente). Coste 0€.
- **B. Añadir un entorno de staging separado para validar la durabilidad antes de producción.**
  Implica infra nueva (otra app/BD) → coste; descartado por la restricción 0€.
- **X. Otra (especifica).**

[Answer]: A

---

## Q5 — Monitorización de la sesión durable (sobre logs de Fly.io, sin infra de pago)

El diseño de observabilidad ya fijó log estructurado JSON (evento/usuario/resultado/correlation-id)
sin herramientas de pago. Aquí decidimos la señal operativa mínima.

- **A. Señal por conteo de logs: seguir `outcome=unrecoverable` (→401) y errores tipados de la
  capa de credencial en los logs de Fly.io; sin dashboard ni alerting dedicado (recomendada).**
  Coste 0€, coherente con NFR-OBS.2. El healthcheck `/health` y el smoke test on-merge existentes
  cubren disponibilidad.
- **B. Añadir alerting/dashboard (servicio de observabilidad).** Implica coste; descartado por 0€.
- **X. Otra (especifica).**

[Answer]: A

---

## Q6 — Migración de datos existentes (sesiones/credenciales en memoria hoy)

Hoy la sesión (y el password en claro) viven solo en memoria; al desplegar, esa memoria se pierde.

- **A. Sin migración de datos: al desplegar, las sesiones en memoria se pierden una vez (los
  usuarios re-loguean) y a partir de ahí son durables; NUNCA se migra el password en claro a la
  BD (recomendada).** Es un corte limpio coherente con FR5 (no persistir la contraseña) y con la
  degradación ya diseñada (401 accionable). Coste 0€, sin script de migración de datos sensibles.
- **X. Otra (especifica).**

[Answer]: A

---

## Consolidated Summary Confirmation

Análisis de ambigüedad: sin respuestas vagas ni contradicciones. Todas las decisiones son concretas
y coherentes (Q1 alimenta el despliegue de Q4; Q2 provee el secreto del diseño de seguridad; Q3
cierra el hueco de FR5).

Resumen de lo que voy a diseñar:

- **Q1 (A) — Tablas nuevas:** script SQL idempotente (`CREATE TABLE IF NOT EXISTS`) versionado en el
  repo, aplicado al arrancar el backend / antes del deploy. Sin herramienta de migraciones nueva.
- **Q2 (A) — Secreto `FUTMONDO_CRED_KEY`:** `fly secrets set` por app, fuera del repo, rotación
  manual documentada en runbook con `scheme` versionado para re-cifrado perezoso. Sin rotación
  automática.
- **Q3 (A) — CI:** añadir gitleaks bloqueante al job `verify` de `fly-deploy.yml` (push→`main`),
  igualándolo al gate de MR. Cierra el hueco de secretos por push directo (FR5/NFR1.4).
- **Q4 (A) — Despliegue:** reutilizar el pipeline actual sin cambios (on-merge: verify →
  deploy-backend → deploy-frontend → smoke `/health`); rollback = redeploy anterior.
- **Q5 (A) — Monitorización:** señal por conteo de logs de Fly.io (`outcome=unrecoverable` y errores
  tipados de credencial); sin dashboard ni alerting dedicado.
- **Q6 (A) — Migración de datos:** ninguna; las sesiones en memoria se pierden una vez (re-login) y
  luego son durables; la contraseña NUNCA se migra a BD.

Voy a generar 4 artefactos: infrastructure-specification, monitoring-design, cicd-pipeline y
traceability.json.

[Answer]: Looks correct
