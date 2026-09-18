# Runbook de Rollback — Backend Security Hardening

> Scope `security-patch`, fase Operation. Complementa y referencia el runbook
> canónico del repo (`docs/ROLLBACK.md`), acotándolo a este release de
> seguridad. Mecanismo: redeploy de la release previa en Fly.io. Coste 0 €.

## Cuándo revertir

- El `smoke-test` post-deploy contra `/health` falla (workflow en rojo).
- Se detecta en producción una regresión funcional o de disponibilidad tras el
  merge de este patch (p. ej. logins que fallan por un cambio inesperado en la
  validación de refresh token — FR9).

## Precondición

- `flyctl` autenticado con acceso a `futmondo-api` (backend) y `futmondo-app`
  (frontend).

## Procedimiento de reversión

1. **Identificar la release previa sana**:
   ```bash
   fly releases --app futmondo-api
   ```
   Anotar la versión (`vN`) anterior a este deploy.

2. **Revertir**:
   ```bash
   fly releases rollback <vN> --app futmondo-api
   ```
   (Repetir para `futmondo-app` solo si el frontend quedó afectado — este patch
   no toca el frontend, así que normalmente basta el backend.)

3. **Verificar salud**:
   ```bash
   curl -sS https://futmondo-api.fly.dev/health   # esperado: HTTP 200 {"status":"healthy"}
   ```

## Pasos de reversión por corrección (si se aísla la causa)

Al ser cambios acotados, un rollback completo revierte las cinco a la vez. Si se
quisiera revertir una sola de forma quirúrgica (vía PR de reverso, no en
caliente):

| FR | Reversión quirúrgica |
|----|----------------------|
| FR6 | Quitar la guarda `price<=0` de `place_bid` (no recomendado: reabre el vector) |
| FR9 | Restaurar el ternario previo de `is_refresh_token_valid` (reabre el bug de rechazo de tokens aware) |
| FR7 | Revertir docstrings de `main.py` (sin efecto funcional) |
| FR8 | Restaurar `SSL_VERIFY=0` en `docker-compose.yml` (solo local) |
| FR18 | Revertir el test añadido (sin cambio de código de producción) |

La vía correcta de reversión quirúrgica es un PR de reverso que pase el gate de
CI, nunca un push directo a `main`.

## Limitaciones conocidas

- El estado en memoria (`TaskManager`, sesiones de sync en curso) se **pierde**
  en cada redeploy/rollback: limitación aceptada del modelo de un único entorno.
- No hay staging: la verificación de release es el smoke test `/health`.

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`); el gate de CI debe
  pasar antes de fusionar.
- Registrar el incidente y la causa raíz.
