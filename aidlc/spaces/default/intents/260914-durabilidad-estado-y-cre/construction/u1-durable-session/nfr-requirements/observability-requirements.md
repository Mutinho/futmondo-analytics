# Observability Requirements — u1-durable-session

> NFR Requirements (Construction), perspectiva operaciones/calidad. A coste 0€, sobre los logs
> de Fly.io existentes; refuerza NFR1 al prohibir loggear secretos.

## Sources

- requirements.md (NFR1, NFR3) [scope]
- functional-design/functional-spec.md (estados rehydrating/active/unrecoverable) [scope]
- nfr-requirements-questions.md (Q4-A) [Q4]

## Requisitos de observabilidad

| ID | Requisito | Detalle | Fuente |
|----|-----------|---------|--------|
| NFR-OBS.1 | **Logging estructurado de eventos de sesión** sin secretos. | Registrar: rehidratación intentada (user_id), resultado (`active` / `unrecoverable`), y emisión de 401 accionable. NUNCA loggear la contraseña ni el material de credencial (refuerza NFR1.1). | NFR1, FR1.2/FR1.3 |
| NFR-OBS.2 | **Sin infraestructura de métricas/tracing de pago.** | Se usan los logs de Fly.io existentes. La señal operativa clave (nº de sesiones no reconstruibles → 401) es derivable de los logs por conteo, sin dashboard dedicado. | NFR3 |

## Notas

- **Anti-patrón evitado**: loggear datos sensibles (PII/credenciales) — explícitamente prohibido
  en NFR-OBS.1.
- **Nivel de log**: `INFO` para transiciones de estado de sesión (evento de negocio), `WARN`
  para `unrecoverable` (degradación esperada), `ERROR` para fallo tipado de descifrado/almacén.
- No se definen SLI/SLO nuevos con alerting dedicado (implicaría infra); la observabilidad es la
  mínima sostenible a coste 0€ que permite operar y auditar el cambio.
