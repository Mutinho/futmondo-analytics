# Observability Design — u1-durable-session

> Etapa NFR Design (Construction). Traduce NFR-OBS.1 y NFR-OBS.2 en un diseño de logging a coste 0€
> sobre los logs de Fly.io existentes. Refuerza NFR1.1 al prohibir loggear secretos.

## Sources

- nfr-requirements/observability-requirements.md (NFR-OBS.1, NFR-OBS.2) [scope]
- functional-design/functional-spec.md (estados rehydrating/active/unrecoverable) [scope]
- nfr-design-questions.md (Q6-A log estructurado JSON con correlation-id) [Q6]
- nfr-requirements/security-requirements.md (NFR1.1 nunca secretos en logs) [scope]

## Estrategia de recogida de métricas

**Sin infraestructura de métricas ni tracing de pago** (NFR-OBS.2, NFR3). No hay Prometheus,
Datadog, X-Ray ni dashboard dedicado. La señal operativa clave — cuántas sesiones acaban en
`unrecoverable` → 401 — se **deriva por conteo** de los logs estructurados en Fly.io (`grep`/filtro).

## Diseño de logging estructurado (NFR-OBS.1)

Log en formato **JSON** por evento de sesión, sobre stdout (lo recoge Fly.io). Campos (Q6-A):

| Campo | Ejemplo | Notas |
|-------|---------|-------|
| `event` | `session.rehydrate` | evento de negocio |
| `user_id` | `"u_123"` | identifica al usuario, no es secreto |
| `outcome` | `active` \| `unrecoverable` | resultado de la transición |
| `correlation_id` | `"req-abc123"` | propagado desde el middleware de petición existente |
| `level` | `INFO`/`WARN`/`ERROR` | ver niveles abajo |

```python
# Ilustrativo (≤15 líneas) — nunca la credencial ni el handle
log.info({
    "event": "session.rehydrate",
    "user_id": user_id,
    "outcome": outcome,            # "active" | "unrecoverable"
    "correlation_id": correlation_id,
})   # PROHIBIDO: password, protected_material, ReauthMaterial
```

### Niveles de log

- `INFO` — transiciones normales de estado de sesión (rehidratación intentada, resultado `active`).
- `WARN` — resultado `unrecoverable` (degradación esperada → 401 accionable).
- `ERROR` — fallo tipado de almacén/resolución de credencial (transitorio, Q4-A), sin el valor sensible.

### Degradación de Q6 (documentada)

Si el backend no tuviera ya un id de petición reutilizable, se emite el mismo log **sin**
`correlation_id` (variante B de Q6). Sigue siendo auditable por conteo de `outcome`; solo se pierde
la traza de punta a punta de la petición. No bloquea el diseño.

## Propagación de correlation-id

Se reutiliza el correlation-id / request-id que el middleware de FastAPI existente ya asigna por
petición. `ensureSession` y `CredentialProtection` lo reciben por contexto y lo incluyen en cada log,
de forma que los eventos de una misma petición se correlacionan en Fly.io. No se añade infraestructura
de tracing distribuido (coste 0€).

## Alertas y escalado

**Sin alerting dedicado** (implicaría infra, NFR-OBS.2/NFR3). La operación es por inspección de logs
bajo demanda. El healthcheck `/health` y el smoke test on-merge existentes cubren la disponibilidad;
esta unidad no cambia esos objetivos.

## SLI/SLO

**No se definen SLI/SLO numéricos nuevos** con alerting. La fiabilidad que aporta el intent (la sesión
ya no se pierde con el reinicio) se verifica por comportamiento (tests), no por un porcentaje de
uptime. Señal observacional disponible por conteo: tasa de `outcome=unrecoverable` sobre rehidrataciones.

## Regla dura de seguridad en logs (refuerzo NFR1.1)

NUNCA se loggea: la contraseña, el `protected_material`, ni el `ReauthMaterial`. Los fallos de la capa
de credencial se registran como error tipado **sin** el valor sensible. gitleaks bloqueante en MR
actúa como red adicional contra secretos que se colaran a disco/logs de repo.

## Trazabilidad

| NFR | Solución de diseño |
|-----|--------------------|
| NFR-OBS.1 | Log estructurado JSON (event/user_id/outcome/correlation_id) de eventos de sesión; niveles INFO/WARN/ERROR; nunca la credencial |
| NFR-OBS.2 | Sin métricas/tracing de pago; señal derivada por conteo de logs Fly.io; sin dashboard |
