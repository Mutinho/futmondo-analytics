# Requisitos de Rendimiento — Backend Security Hardening

> Scope `security-patch`, depth Minimal. Las correcciones no deben degradar el rendimiento actual.

## Presupuesto de Latencia (no regresión)

- **NFR-PERF.1** (FR6): La validación de `price` en `place_bid` es una comprobación en memoria (entero > 0) que se ejecuta **antes** del proxy a Futmondo; su coste es despreciable (< 1 ms) y no añade ninguna llamada de red. Rechazar una entrada inválida es más rápido que hoy (se evita la llamada saliente). Traza: FR6.
- **NFR-PERF.2** (FR9): La corrección de `is_refresh_token_valid` no cambia el número de consultas a la base de datos (misma `SELECT`); solo corrige la evaluación del ternario. Sin impacto en la latencia de `/auth/refresh`.

## Objetivos Generales

- **NFR-PERF.3**: Ninguna corrección introduce trabajo síncrono adicional en el camino caliente de una petición autenticada. El comportamiento observable de latencia de los endpoints afectados se mantiene igual o mejora. No hay target numérico nuevo: el intent es de seguridad, no de rendimiento.

## Assumptions & Open Questions

None. Detalle de superficie afectada en `security-requirements.md` (cross-referencia).

## Notas

Sin benchmarks nuevos requeridos para este scope. Ver `reliability-requirements.md` para la garantía de suite verde y `security-requirements.md` para los targets funcionales de cada FR.

<!-- Re-anclado 2026-09-17 (redo-jump; contenido sin cambios). -->

<!-- Re-guardado 2026-09-17 tras confirmación vigente (contenido sin cambios). -->
