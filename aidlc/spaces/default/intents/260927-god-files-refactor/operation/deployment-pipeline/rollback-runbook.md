# Runbook de Rollback — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, brownfield. Conversation language: Spanish.
>
> Procedimiento **vigente** documentado en `docs/ROLLBACK.md`. Este runbook lo referencia y lo aplica a la Oleada 1. El rollback es a nivel de release de Fly.io, ajeno a la estructura interna del código extraído.

## Cuándo hacer rollback

- El smoke test post-deploy contra `/health` falla (el workflow marca el release en rojo).
- Se detecta en producción un error funcional o de disponibilidad tras un merge a `main` (p. ej. una divergencia de payload en un endpoint analytics — que la caracterización debería haber prevenido, pero el rollback es la red de seguridad).

## Precondición

`flyctl` autenticado con acceso a `futmondo-api` (backend) y `futmondo-app` (frontend).

## Procedimiento (Fly.io — redeploy de la release previa)

### 1. Identificar la release estable previa

```bash
fly releases --app futmondo-api    # backend (contiene la extracción de analytics)
fly releases --app futmondo-app    # frontend (sin cambios en esta oleada)
```

Anota la versión `vN` de la última release sana (anterior al deploy problemático).

### 2. Revertir

```bash
# Opción A (recomendada):
fly releases rollback <vN> --app futmondo-api
# Opción B (si rollback no está disponible): redeploy explícito de la imagen previa
fly deploy --app futmondo-api --image <registry.fly.io/futmondo-api:deployment-XXXX>
```

En esta oleada el cambio es solo backend (`analytics/` + shim); normalmente basta revertir `futmondo-api`. Revertir `futmondo-app` solo si un deploy de frontend coincidente quedó afectado.

### 3. Verificar salud

```bash
curl -sS https://futmondo-api.fly.dev/health   # esperado: HTTP 200, {"status":"healthy"}
```

## Disparadores de rollback

- Fallo del smoke test `/health` (automático en el workflow: el job queda en rojo).
- Regresión observable reportada tras el merge.

## Limitaciones conocidas (heredadas)

- El estado en memoria (`TaskManager`, sesiones de sync en curso) se pierde en cada redeploy/rollback (modelo de un único entorno). Los syncs en curso se relanzan tras el rollback.
- Sin staging: la verificación de release es el smoke test `/health`.

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`); el gate de CI debe pasar antes de fusionar.
- Registrar el incidente y la causa raíz.

## Referencia

Fuente de verdad del procedimiento: `docs/ROLLBACK.md` (no modificado por esta oleada).
