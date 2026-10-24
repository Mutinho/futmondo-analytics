# Deployment Pipeline — Preguntas

Intent `261023-sync-jugador-completo`. El proyecto YA tiene un pipeline Fly.io
maduro (`.github/workflows/fly-deploy.yml`: `verify → deploy-backend →
deploy-frontend → smoke-test`, región `cdg`, apps `futmondo-api` + `futmondo-app`,
healthcheck `/health`) y un runbook de rollback (`docs/ROLLBACK.md`). Este intent
es un cambio de backend que **no toca** el pipeline; estas preguntas fijan cómo
se despliega el cambio a través de lo existente. Cada ⭐ es la recomendación.

---

## Q1. Estrategia de despliegue del cambio

- A. ⭐ **Deploy-on-merge existente, sin cambios**: al mergear a `main`,
  `fly-deploy.yml` corre `verify` (gate bloqueante) → `deploy-backend` →
  `deploy-frontend` → `smoke-test` (`/health`, 5 reintentos). No se introduce
  blue/green ni canary nuevos (no aplican al tier Fly.io free; el redeploy de
  Fly.io ya hace rolling con healthcheck). El cambio es solo backend.
- X. Other (please specify)

[Answer]: A

---

## Q2. Migración de esquema en el despliegue

- A. ⭐ La migración (`ALTER TABLE players ADD COLUMN`) se aplica **manualmente y
  directamente contra Neon** (ya ejecutada y verificada: las 6 columnas
  presentes), ANTES del deploy del código que las usa. No se deja en el arranque
  (`ensure_schema_updates`): el `ALTER` idempotente se **retiró** del código
  (migración solo-manual, decisión del propietario). Es no destructiva
  (columnas añadidas con default), así que un rollback del código no necesita
  revertir el esquema; el código viejo ignora las columnas nuevas.
- X. Other (please specify)

[Answer]: A

---

## Q3. Población de los campos nuevos tras el deploy

- A. ⭐ Los campos nuevos quedan con su default hasta el **primer sync de
  jugadores** (que ya corre periódicamente y bajo demanda). No se fuerza un sync
  en el release; se puede lanzar un sync manual tras el deploy para poblarlos de
  inmediato si se desea (opcional, no bloqueante). Mientras, `favorites/my`
  degrada con los defaults (como hoy).
- X. Other (please specify)

[Answer]: A

---

## Q4. Rollback

- A. ⭐ **Runbook existente** (`docs/ROLLBACK.md`): redeploy de la release Fly.io
  anterior. La migración es no destructiva (columnas añadidas), así que revertir
  el código no requiere tocar el esquema; el código viejo ignora las columnas
  nuevas. Sin pasos de rollback de datos.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen (Todas A, Q2 ajustado):
- Q1 Deploy-on-merge Fly.io existente sin cambios.
- Q2 Migración aplicada MANUALMENTE a Neon (6 columnas verificadas); ALTER de arranque retirado (solo-manual); no destructiva.
- Q3 Campos con default hasta el primer sync; sync manual opcional tras el deploy.
- Q4 Rollback por runbook existente (redeploy); sin rollback de datos.

[Answer]: Looks correct
