# Runbooks — Durabilidad del estado (coste 0 €)

> Etapa Incident Response (Operation). Runbooks para los modos de fallo nuevos de la durabilidad, con
> las herramientas gratuitas de Fly.io + Neon. Sin SSM Automation ni remediación automatizada de pago;
> los pasos son manuales para un operador. Cada runbook incluye pasos de reversión.

## RB-1: Sesiones no se rehidratan tras reinicio (FR1.2)

**Síntoma**: usuarios reportan re-login inesperado tras un redeploy; `fly logs` muestra 401 tras reinicio.

1. Verificar que el secret existe: `fly secrets list --app futmondo-api` (buscar `FUTMONDO_CRED_KEY`).
2. Si falta, fijarlo:
   ```bash
   fly secrets set FUTMONDO_CRED_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" --app futmondo-api
   ```
   (fijar un secret dispara redeploy de la máquina).
3. Confirmar en `fly logs` que cesan los fallos de descifrado y las sesiones se rehidratan.

**Reversión**: si la clave nueva causa problemas, el impacto es que los usuarios re-loguean (degradación segura). No hay estado que revertir; el password nunca se persiste.

## RB-2: Error de descifrado del handle de sesión

**Síntoma**: `fly logs` muestra `InvalidToken`/`Fernet` al rehidratar (clave rotada o corrupta).

1. Es esperado tras rotar `FUTMONDO_CRED_KEY`: los handles cifrados con la clave anterior quedan
   invalidados; cada usuario re-loguea una vez y se re-cifra con la clave nueva.
2. Si NO se rotó la clave y aparece igualmente, revisar que el secret no se haya truncado/mal copiado;
   re-fijar con una clave válida (RB-1 paso 2).

**Reversión**: no aplicable — la contraseña no se persiste; el peor caso es re-login del usuario.

## RB-3: Tareas de sync huérfanas tras redeploy (FR1.5)

**Síntoma**: tras un redeploy, una tarea aparecía "en curso".

1. **No requiere intervención**: el arranque ejecuta `mark_interrupted_on_startup`, que marca las
   tareas en curso como `interrupted_by_restart` (FR1.5). El usuario puede relanzarlas (FR1.6).
2. Verificar en `fly logs` que el sweep de arranque corrió: `grep interrupted_by_restart`.
3. Si una tarea sigue mostrándose "en curso" indefinidamente, revisar que el sweep no falló al arrancar.

**Reversión**: no aplicable — es marcado de estado, no una operación destructiva.

## RB-4: Backend caído / healthcheck en rojo

**Síntoma**: `/health` no responde 200; smoke test o dashboard de Fly.io en rojo.

1. Fly.io reinicia la máquina automáticamente ante 3 fallos consecutivos del check.
2. Si persiste: `fly logs --app futmondo-api` para diagnosticar (¿guard `JWT_SECRET`? ¿conexión Neon?).
3. Comprobar arranque: si aborta por `JWT_SECRET` default/vacío (NFR1.1), fijar el secret correcto.
4. Si el problema es del release, ejecutar rollback (RB-5).

**Reversión**: rollback al release anterior (RB-5).

## RB-5: Rollback de release

1. Seguir `docs/ROLLBACK.md`: redeploy de la release anterior en Fly.io.
2. El esquema durable es aditivo e idempotente: un rollback de la app **no** requiere rollback de BD.
3. Verificar `/health` = 200 y `fly status` tras el rollback.

**Reversión del rollback**: re-desplegar la release más nueva cuando el fix esté listo.

## RB-6: Errores de persistencia contra Neon

**Síntoma**: `fly logs` muestra `TaskPersistenceError` o errores de conexión.

1. Verificar el estado de Neon (dashboard de Neon) y que `DATABASE_URL` es correcto
   (`fly secrets list`).
2. El estado durable degrada con seguridad: `TaskManager` como caché best-effort mantiene la operación
   básica; las lecturas fallan hacia error tipado, no hacia estado corrupto.
3. Restaurar conectividad a Neon; no hay pasos destructivos.

**Reversión**: no aplicable.
