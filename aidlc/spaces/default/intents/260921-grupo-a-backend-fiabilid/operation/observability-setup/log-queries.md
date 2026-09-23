# Consultas de logs — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: en vez de CloudWatch
> Logs Insights, se usan `fly logs` + filtrado local (`grep`), a coste 0 €. El
> logging estructurado del intent (`record_degraded_step`) hace estas consultas
> significativas.

## Consultas clave (Fly.io + grep)

Paso de sync degradado (la señal central del intent, FS1/FR3.1):

```bash
fly logs --app futmondo-api | grep "sync step degraded"
# Campos estructurados emitidos: sync_step=<paso>, reason=<motivo>
```

Rechazos de puja por techo/positividad (FR6/NFR5):

```bash
fly logs --app futmondo-api | grep -Ei "market/bid|precio de la puja"
```

Errores de arranque/migraciones que se propagan (FR3.2 — ya no se tragan):

```bash
fly logs --app futmondo-api | grep -Ei "Migration|column/object already exists|pool"
```

Salud del servicio:

```bash
fly status --app futmondo-api
curl -sS https://futmondo-api.fly.dev/health
```

## Formato de log del intent

- `record_degraded_step` emite `logger.warning("sync step degraded", extra={"sync_step": step, "reason": reason})`.
  El texto fijo `sync step degraded` es el ancla de búsqueda; `sync_step` y
  `reason` dan el detalle. Esto permite localizar sin dashboard qué paso se
  degradó y por qué.

## NO-APLICA / diferido (servicios de pago)

- CloudWatch Logs Insights, agregación gestionada con consultas guardadas y
  retención larga: diferidos. `fly logs` (streaming, retención corta) cubre la
  necesidad del intent a coste 0 €.

## Sources

- `construction/sync-reliability/functional-design/functional-spec.md` (FS1,
  formato del log), `construction/sync-reliability/code-generation/code-summary.md`.

## Assumptions & Open Questions

None.
