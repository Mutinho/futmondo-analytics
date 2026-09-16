# Load Test Plan — Durabilidad del estado (coste 0 €)

> Etapa Performance Validation (Operation). Plan de validación bajo carga. **No se ejecuta carga real
> en este intent**: NFR2 no tiene umbral numérico definido y no hay entorno de staging ni herramienta
> de carga a coste 0 €. Este plan documenta cómo se validaría si se fijara un umbral, de modo que la
> validación quede completamente preparada para el futuro.

## Precondición: definir el umbral NFR2

La validación bajo carga solo tiene sentido contra un objetivo. Antes de ejecutar, fijar en
`nfr-requirements` un umbral medible, p. ej.:

- Latencia del camino de sesión (`/auth/refresh`, primera petición autenticada tras reinicio):
  p95 < X ms.
- Latencia de `/api/v1/sync/task/{id}` (lectura de tarea durable): p95 < Y ms.

Sin ese umbral, la carga produce números sin criterio de pase/fallo.

## Plan (cuando se fije el umbral)

| Aspecto | Enfoque coste 0 € |
|---------|-------------------|
| Herramienta | k6 o locust (OSS, gratuitas), ejecutadas desde local o una máquina Fly one-shot |
| Entorno | Staging efímero (app Fly.io temporal) o ventana controlada; NUNCA carga destructiva contra la única máquina de producción sin coordinar |
| Escenarios | Ramp-up (0→N usuarios), steady-state (peak sostenido), y específico de durabilidad: rehidratación de sesión tras reinicio bajo concurrencia |
| Métricas | p50/p95/p99 de latencia, throughput (RPS), tasa de error, uso de memoria (256 MB) |
| Foco durabilidad | Lectura de tarea durable (caché→BD), rehidratación de sesión (descifrado Fernet), unicidad 409 bajo concurrencia (relevante a R-01 de u2) |

## Escenario específico recomendado (durabilidad)

- **Concurrencia en `/trigger`**: lanzar múltiples `/trigger` concurrentes del mismo `championship_id`
  para ejercitar la ventana SELECT→INSERT (hallazgo R-01 de u2). Con `min=max=1` la ventana es
  estrecha; este escenario la mediría si se escalara a >1 instancia.

## Estado

- **NO EJECUTADO** en este intent (sin umbral, sin entorno de carga a coste 0 €). Plan listo para
  cuando se defina el umbral o se graduara a un tier con capacidad de prueba.
