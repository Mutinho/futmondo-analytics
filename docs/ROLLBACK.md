# Runbook de Rollback (Fly.io)

> NFR2.2. Entorno único de producción en Fly.io (sin staging separado). El
> rollback es **manual**: se vuelve a desplegar la imagen previa. Este runbook
> es el procedimiento mínimo documentado.

## Cuándo hacer rollback

- El smoke test post-deploy contra `/health` falla (el workflow de deploy lo
  marca en rojo).
- Un error funcional o de disponibilidad se detecta en producción tras un merge
  a `main`.

## Precondición

- `flyctl` autenticado (`fly auth login`) con acceso a las apps `futmondo-api`
  (backend) y `futmondo-app` (frontend).

## Procedimiento

### 1. Identificar la release estable previa

```bash
fly releases --app futmondo-api        # backend
fly releases --app futmondo-app        # frontend
```

Anota el número de versión (`vN`) de la última release sana (la anterior al
deploy problemático).

### 2. Revertir a la imagen previa

Opción A — rollback directo de la release (recomendado):

```bash
fly releases rollback <vN> --app futmondo-api
```

Opción B — redeploy explícito de la imagen previa (si `rollback` no está
disponible en tu versión de flyctl):

```bash
# Localiza la imagen previa en la salida de `fly releases --image`
fly deploy --app futmondo-api --image <registry.fly.io/futmondo-api:deployment-XXXX>
```

Repite para `futmondo-app` si el frontend también quedó afectado.

### 3. Verificar salud tras el rollback

```bash
curl -sS https://futmondo-api.fly.dev/health
# Esperado: {"status":"healthy"}
```

Debe devolver HTTP 200 y `{"status":"healthy"}`. Si sigue en rojo, escala el
incidente y considera detener la máquina (`fly machine stop`) mientras se
diagnostica.

## Limitaciones conocidas

- El estado en memoria (`TaskManager`, sesiones de sync en curso) se **pierde**
  en cada redeploy/rollback: es una limitación aceptada del modelo de un único
  entorno. Los syncs en curso deberán relanzarse tras el rollback.
- No hay staging: la verificación de release es el smoke test `/health`.

## Post-rollback

- Abre un PR con el fix real (nunca push directo a `main`): el gate de CI debe
  pasar antes de fusionar (ver `docs/PR-GATE.md`).
- Registra el incidente y la causa raíz para no repetir el fallo.
