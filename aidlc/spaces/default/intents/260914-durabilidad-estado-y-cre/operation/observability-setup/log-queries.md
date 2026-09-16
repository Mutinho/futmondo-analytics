# Log Queries — Durabilidad del estado (coste 0 €)

> Etapa Observability Setup (Operation). Consultas concretas sobre `fly logs` (backend `futmondo-api`)
> para observar las señales operativas de la durabilidad. Coste 0 € — sin sistema de log aggregation
> de pago. Se recomienda logging estructurado para que estos filtros sean fiables.

## Comando base

```bash
# Logs en tiempo real
fly logs --app futmondo-api

# Volcar y filtrar (ejemplo con grep local)
fly logs --app futmondo-api | grep -iE "session|task|401|409|error"
```

## Señales de durabilidad de sesión (u1)

```bash
# Fallos de rehidratación / descifrado de credencial (FUTMONDO_CRED_KEY ausente o rotada)
fly logs --app futmondo-api | grep -iE "reauth|decrypt|credential|InvalidToken|Fernet"

# 401 accionables tras reinicio (FR1.3) — esperado tras rotación de clave o si el secret falta
fly logs --app futmondo-api | grep -E "401"
```

## Señales de durabilidad de tareas (u2)

```bash
# Tareas marcadas interrumpidas por reinicio al arranque (FR1.5) — pico correlaciona con redeploy
fly logs --app futmondo-api | grep -iE "interrupted_by_restart|mark_interrupted"

# Conflictos de unicidad 409 en /trigger (FR1.6)
fly logs --app futmondo-api | grep -E "409|TaskConflictError"

# Errores de persistencia de tarea
fly logs --app futmondo-api | grep -iE "TaskPersistenceError"
```

## Arranque / esquema

```bash
# Creación idempotente del esquema durable y sweep de arranque
fly logs --app futmondo-api | grep -iE "ensure_durable|schema|startup"

# Guard de arranque JWT (NFR1.1) — no debe abortar en producción
fly logs --app futmondo-api | grep -iE "JWT_SECRET|FATAL"
```

## Recomendación (coste 0 €)

- **Logging estructurado**: emitir estas transiciones con un prefijo/campo estable (p. ej.
  `event=session_rehydrated`, `event=task_interrupted_on_restart`) para que los filtros sean precisos
  y no dependan de prosa libre. Es una mejora de coste 0 € que hace la observabilidad por logs fiable.
- **Retención**: `fly logs` es efímero (no persiste histórico largo). Para retención sin coste,
  redirigir a un destino gratuito queda como mejora futura opcional; hoy la observación es en vivo /
  reciente.

## No-aplica a coste 0 €

CloudWatch Logs Insights, índices full-text y retención gestionada de 90 días+ requieren
infraestructura de pago. Diferido; la alternativa gratuita es `fly logs` + grep como arriba.
