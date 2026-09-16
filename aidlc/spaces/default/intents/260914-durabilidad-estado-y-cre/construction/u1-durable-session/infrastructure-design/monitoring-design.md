# Monitoring Design — u1-durable-session

> Etapa Infrastructure Design (Construction). Implementa la estrategia de `observability-design`
> (NFR Design) sobre la plataforma real: **logs de Fly.io**, sin métricas/tracing de pago (NFR-OBS.2,
> coste 0€). Q5-A: señal por conteo de logs; sin dashboard ni alerting dedicado.

## Sources

- nfr-design/observability-design.md (log estructurado JSON; niveles; nunca secretos) [scope]
- nfr-design/reliability-design.md (estados unrecoverable/401; error tipado) [scope]
- team.md (healthcheck `/health`, smoke test on-merge) [scope]
- infrastructure-design-questions.md (Q5-A señal por conteo, sin dashboard/alerting) [Q5]

## Metrics & KPIs

Sin sistema de métricas dedicado; los "KPIs" son **derivables por conteo** de los logs estructurados
en Fly.io (`grep`/filtro por campo `event`/`outcome`).

| Metric | Source | Threshold | Why it matters |
|--------|--------|-----------|----------------|
| Nº de rehidrataciones con `outcome=unrecoverable` (→401) | Logs Fly.io (`event=session.rehydrate`, `outcome=unrecoverable`) | Sin umbral automático; revisión bajo demanda | Señal principal: sesiones que no se pudieron reconstruir (FR1.3); un pico indica handles caducados/inválidos |
| Nº de errores tipados de la capa de credencial | Logs Fly.io (`level=ERROR`, error de descifrado/almacén) | Sin umbral automático | Distingue fallo transitorio (Q4-A) de degradación normal; un pico sugiere problema con `FUTMONDO_CRED_KEY` o Neon |
| Disponibilidad del backend | Healthcheck `/health` (Fly.io) + smoke test on-merge | HTTP 200 (smoke reintenta 5x) | Cubre disponibilidad; sin cambios respecto a hoy |

## Alerts

| Alert | Condition | Severity | Routes to |
|-------|-----------|----------|-----------|
| (ninguna dedicada) | Sin alerting automático (Q5-A/NFR-OBS.2: implicaría infra de pago) | — | Inspección manual de logs de Fly.io bajo demanda |
| Fallo de release (existente) | Smoke test `/health` no devuelve 200 tras 5 reintentos on-merge | Bloquea el release | Job de CI (fallo visible en GitHub Actions) |

No se añade alerting nuevo: sería un servicio de pago. La única "alerta" es la ya existente del smoke
test que bloquea el despliegue.

## SLIs / SLOs

| SLI | SLO target | Measurement window |
|-----|-----------|--------------------|
| (ninguno numérico nuevo) | Sin SLA/SLO de disponibilidad numérico nuevo (reliability-design) | — |
| Reconstruibilidad de sesión (cualitativa) | 100% de sesiones válidas con medio de re-auth reconstruibles tras reinicio | Verificada por test, no por porcentaje de uptime |

La fiabilidad que aporta la unidad (la sesión ya no se pierde con el reinicio) se verifica por
comportamiento (tests), no por un número de uptime; no se define un SLO nuevo con alerting.

## Logs & Tracing

- **Agregación de logs:** stdout del contenedor `futmondo-api`, recogido por Fly.io. Sin exportador
  a un servicio externo (coste 0€).
- **Formato:** JSON estructurado por evento de sesión — campos `event`, `user_id`, `outcome`,
  `correlation_id`, `level` (observability-design). Si el backend no tuviera ya un id de petición
  reutilizable, se emite sin `correlation_id` (degradación documentada), sin bloquear.
- **Niveles:** `INFO` transiciones normales; `WARN` `unrecoverable` (degradación esperada); `ERROR`
  fallo tipado de descifrado/almacén.
- **Regla dura:** NUNCA se loggea la contraseña, el handle (cifrado o descifrado) ni
  `protected_material`. El tipo que transporta material sensible tiene `__repr__` redactado (control
  determinista de security-design).
- **Tracing:** sin tracing distribuido de pago (NFR-OBS.2). La correlación por petición se logra con
  el `correlation_id` en cada log, suficiente para seguir una petición en Fly.io.
- **Dashboards:** ninguno dedicado (Q5-A). La operación es por consulta/filtro de logs.

## Trazabilidad

| NFR | Solución de monitorización |
|-----|----------------------------|
| NFR-OBS.1 | Log estructurado JSON de eventos de sesión (event/user_id/outcome/correlation_id) en Fly.io; niveles INFO/WARN/ERROR; nunca la credencial |
| NFR-OBS.2 | Sin métricas/tracing/alerting de pago; señal por conteo de logs; sin dashboard |
