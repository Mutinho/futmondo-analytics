# Log Queries — F1: Login nativo end-to-end

> Fase: operación (observability-setup). Idioma: castellano; comandos verbatim en inglés. Sin
> CloudWatch Logs Insights (de pago). Las "saved queries" son recetas `fly logs` + `grep`/`awk`
> gratuitas. Coste 0 €.

## Consultas guardadas (fly logs + grep)

| Nombre | Comando | Uso |
|--------|---------|-----|
| Actividad de auth | `fly logs --app futmondo-api \| grep -E "/auth/(login\|refresh\|logout)"` | Ver el flujo de login/refresh/logout |
| Errores de auth | `fly logs --app futmondo-api \| grep -E "/auth/" \| grep -E "( 4[0-9]{2}\| 5[0-9]{2})"` | Fallos de credencial / transporte del token |
| Errores del servidor | `fly logs --app futmondo-api \| grep -E "( 5[0-9]{2}\|Traceback\|ERROR)"` | Caídas / excepciones |
| Arranque / JWT | `fly logs --app futmondo-api \| grep -iE "(startup\|JWT_SECRET\|healthy)"` | Verificar arranque sano (JWT no-default) |

## Buenas prácticas de logging (para que `grep` sustituya a las consultas gestionadas)

- Preferir **logs estructurados** con campos estables (p. ej. `endpoint`, `status`, `reason`,
  `task_id`) para que `grep`/`awk` filtren de forma fiable.
- **NUNCA** registrar el refresh token, el access token, el password ni el token Futmondo del
  usuario (ni en mensaje, `repr` ni `exc_info`): guardarraíl de seguridad durable de D-01. Los logs
  llevan contexto no sensible (status, endpoint), nunca material de credencial.

## Retención

- La retención de `fly logs` es la del tier gratuito de Fly.io (stream reciente; sin archivado
  gestionado). Archivado/retención larga gestionada = **NO-APLICA** (de pago). Para incidentes, el
  mantenedor captura el extracto relevante manualmente.

## NO-APLICA (de pago)

| CloudWatch Logs Insights / stage | Estado |
|---|---|
| Saved queries gestionadas con agregación | NO-APLICA; sustituido por recetas `fly logs`+`grep` |
| Retención/archivado gestionado | NO-APLICA (tier gratuito) |

## Sources

- [consumes] monitoring-design.md, security-design.md — NO existen (`skipped`); derivado de la app
  desplegada.
- [memory] aidlc-shared/operation-fly-stack.md (logging estructurado + `fly logs`); project.md
  (NUNCA credenciales/tokens en logs; coste 0 €).

## Assumptions & Open Questions

None.
