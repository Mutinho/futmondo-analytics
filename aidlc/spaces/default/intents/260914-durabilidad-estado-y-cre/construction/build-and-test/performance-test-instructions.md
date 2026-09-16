# Performance Test Instructions — Durabilidad del estado

> Etapa Build and Test (Construction). Estrategia **Standard**. NFR2 (rendimiento) no fija un umbral
> numérico en esta etapa (decisión de requirements: "se validará por medición en diseño/build"). Este
> archivo documenta el enfoque y por qué no hay una prueba de carga bloqueante local. Coste 0 €.

## Requisito de rendimiento (NFR2)

- **NFR2**: la persistencia de sesión y de estado de tareas no debe degradar de forma perceptible el
  camino de sesión. **Sin umbral numérico** fijado en requirements/diseño.

## Enfoque de validación

- **No se ejecuta prueba de carga (load/stress) en esta etapa.** No hay un objetivo numérico contra
  el que medir, y una carga real requeriría un entorno productivo (Neon + Fly.io), fuera del alcance
  de coste 0 € de tests locales con fakes.
- El impacto de rendimiento es acotado por diseño: una lectura/escritura adicional a la capa
  `stores/` en el camino de sesión/tarea, con la BD como autoridad y el caché en memoria como
  best-effort (evita golpear BD en el camino caliente cuando el caché está poblado).
- La suite completa (125 tests) corre en < 1 s con fakes, lo que confirma que la lógica añadida no
  introduce coste algorítmico anómalo a nivel unitario/integración.

## Estado del objetivo NFR2

- **Verdict: Unverified (diferido)** — no hay umbral numérico ni etapa de validación de rendimiento
  programada en el plan de ejecución de este intent (scope `feature`; `performance-validation` es una
  etapa de Operación que este scope ejecuta pero sin objetivo numérico definido aquí). Se recomienda,
  si se quiere cerrar formalmente, fijar un umbral (p. ej. p95 del camino `/auth/refresh`) y medirlo
  con carga en un entorno productivo en una intervención posterior.

## Cómo se mediría (si se define un umbral)

```bash
# Ejemplo (NO ejecutado aquí): medir latencia del camino de sesión con carga controlada
# contra un entorno productivo, comparando antes/después de la durabilidad.
# Herramienta sugerida coste 0: k6 o locust contra staging efímero.
```
