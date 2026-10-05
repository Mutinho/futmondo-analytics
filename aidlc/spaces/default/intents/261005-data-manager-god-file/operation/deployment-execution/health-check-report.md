# Health Check Report — refactor `data_manager_v2`

Validación de health checks para el deploy on-merge. El refactor **no cambia** la
configuración de health checks ni la topología; se registran los checks
existentes y la expectativa de equivalencia.

## Health checks existentes (sin cambios)

| Componente | App Fly.io | Check | Esperado |
|---|---|---|---|
| Backend API | `futmondo-api` | `/health` (puerto 8000) | HTTP 200, `{"status":"healthy"}` |
| Frontend | `futmondo-app` | `/` (nginx, puerto 80) | HTTP 200 |
| Base de datos | Neon PostgreSQL (Frankfurt, free) | conectividad vía backend | reachable |

## Validación disponible a coste 0 (mapeo Fly.io)

Según `operation-fly-stack.md`: observación pull (`fly status`, `fly logs`,
healthcheck `/health`). Sin CloudWatch/X-Ray (de pago, NO-APLICA). SLI informal =
`/health` 200 + ausencia de pasos `degraded` inesperados en `fly logs`.

## Expectativa de equivalencia (refactor)

- El refactor es de capa de datos interna (descomposición de `DataManagerV2`);
  no toca los endpoints, la auth, ni las integraciones externas.
- Comportamiento observable **nulo**: mismos endpoints, mismos payloads. Los
  health checks deben seguir verdes sin cambio.
- La red de seguridad local (414 tests verdes, cobertura 57.48%) cubre la
  equivalencia de los `get_*`/`save_*` que alimentan los endpoints servidos.

## Estado

**PENDIENTE (on-merge).** La validación en vivo de los health checks se produce
tras el deploy on-merge; no se ejecuta un deploy manual desde esta etapa. Sin
findings de salud que reportar en este punto (no hay cambio de infraestructura
ni de contrato de salud).

## Observabilidad post-deploy (recordatorio)

Tras el merge, verificar `fly logs --app futmondo-api` para confirmar arranque
limpio (sin errores de import de los nuevos módulos `data_manager/`) y ausencia
de excepciones nuevas en los primeros syncs/lecturas.
