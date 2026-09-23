# Configuración de SLO/SLI — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: Fly.io + Neon, coste
> 0 €. SLOs formales con burn-rate **NO-APLICA/diferido** (requieren backend de
> métricas de pago). Se documenta un SLI informal observable con las
> herramientas gratuitas.

## SLI informal (observable a coste 0 €)

| SLI | Definición | Fuente gratuita |
|---|---|---|
| Disponibilidad backend | `/health` responde 200 | `smoke-test` post-deploy; `curl` puntual |
| Fiabilidad de la sync | proporción de ejecuciones de sync sin pasos `degraded` inesperados | inspección de `fly logs` (`sync step degraded`) |

- No se computa un objetivo porcentual con ventana temporal (eso exige métricas
  agregadas de pago). El SLI es una señal cualitativa: `/health` verde y ausencia
  de `degraded` no explicados.

## SLO formal — NO-APLICA / diferido

- Un SLO cuantificado (p. ej. "99,9 % de disponibilidad en 30 días") con
  alerting por **burn-rate** requiere un backend de métricas con retención e
  historización (servicio de pago). Queda **diferido** conforme al mandato de
  coste 0 € y a la regla de adaptación de stack de `project.md`.
- Alternativa gratuita vigente: el healthcheck de Fly.io + `smoke-test` como
  verificación de release, y `fly logs` para la señal de fiabilidad de la sync.

## Relación con el intent

- El intent **mejora** el SLI de fiabilidad: al marcar `degraded` (en vez de
  `done`) un paso non-critical que falla, la señal de fiabilidad deja de estar
  falseada (un fallo ya no se cuenta como éxito). Esto es precisamente NFR1
  (fiabilidad observable).

## Sources

- `inception/requirements-analysis/requirements.md` (NFR1),
  `construction/sync-reliability/functional-design/rules.md` (BR1-BR3),
  `project.md` (adaptación de stack Operation + coste 0 €).

## Assumptions & Open Questions

None.
