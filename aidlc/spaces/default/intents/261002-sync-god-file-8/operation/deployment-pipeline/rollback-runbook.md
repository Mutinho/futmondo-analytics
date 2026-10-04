# Rollback Runbook — Fly.io (sync domain decomposition refactor)

Runbook de rollback para el despliegue de este refactor. Alinea con el runbook
canónico del repo (`docs/ROLLBACK.md`) y añade las notas específicas del intent.
El mecanismo Fly.io es **redeploy de la release previa** (rollback manual).

## Fuentes

- Runbook canónico: `docs/ROLLBACK.md`
- Pipeline: `.github/workflows/fly-deploy.yml` (ver `cd-config.md`,
  `deployment-strategy.md`)
- Adaptación de stack: `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`

## Disparadores de rollback

- El `smoke-test` post-deploy contra `/health` falla (el workflow queda en rojo).
- Un error funcional o de disponibilidad se detecta en producción tras el merge.
- **Específico del refactor**: cualquier desviación observable en el resultado de
  un sync (`SyncResult`) o en `sync_all()` respecto al comportamiento previo
  (aunque la equivalencia estricta y las characterization tests lo hacen
  improbable). El indicador operativo: pasos de sync marcados como fallidos/raros
  en `fly logs`, o `/health` en rojo.

## Precondición

- `flyctl` autenticado con acceso a `futmondo-api` (backend) y `futmondo-app`
  (frontend).

## Procedimiento

### 1. Identificar la release estable previa

```bash
fly releases --app futmondo-api        # backend (donde vive este refactor)
fly releases --app futmondo-app        # frontend (sin cambios en este intent)
```

Anota la `vN` de la última release sana (anterior al deploy del refactor).

### 2. Revertir a la imagen previa

```bash
# Opción A (recomendada): rollback directo de la release
fly releases rollback <vN> --app futmondo-api

# Opción B (si rollback no está disponible en tu flyctl): redeploy explícito
fly deploy --app futmondo-api --image registry.fly.io/futmondo-api:deployment-XXXX
```

Como el refactor es **backend-only**, normalmente basta revertir `futmondo-api`;
`futmondo-app` no cambió en este intent.

### 3. Verificar salud tras el rollback

```bash
curl -sS https://futmondo-api.fly.dev/health   # Esperado: HTTP 200 {"status":"healthy"}
```

Si sigue en rojo, escala el incidente y considera `fly machine stop` mientras se
diagnostica.

## Alcance del rollback para este refactor

- Revertir restaura el `data_sync_service.py` monolítico previo (los dominios
  extraídos desaparecen con la imagen anterior) y es seguro: la superficie
  pública es idéntica, así que ningún consumidor (router worker) se rompe al
  volver atrás.
- No hay rollback de datos: el refactor no cambió esquema ni escribió datos
  nuevos (no hay migración que deshacer).

## Limitaciones conocidas

- El estado en memoria (`TaskManager`, syncs en curso) se pierde en el
  redeploy/rollback (limitación aceptada del modelo de un único entorno); los
  syncs en curso se relanzan tras el rollback.
- Sin staging: la verificación de release/rollback es el smoke test `/health`.
- Observabilidad a coste 0 €: diagnóstico vía `fly logs` + `fly status`
  (sin alarmas gestionadas ni auto-rollback; el rollback es manual).

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`); el gate de CI debe
  pasar antes de fusionar.
- Registrar el incidente y la causa raíz.
