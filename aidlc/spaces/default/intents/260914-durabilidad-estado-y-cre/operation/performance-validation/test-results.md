# Performance Test Results — Durabilidad del estado

> Etapa Performance Validation (Operation). **No se ejecutó una prueba de carga** (sin umbral NFR2, sin
> entorno de carga a coste 0 €). Este documento recoge la evidencia cualitativa disponible y el estado
> real, sin fabricar métricas de carga.

## Estado: SIN CARGA EJECUTADA — análisis cualitativo

- No hay resultados de latencia/throughput bajo carga porque no se ejecutó carga (ver `load-test-plan.md`).

## Evidencia cualitativa disponible

| Evidencia | Resultado | Interpretación |
|-----------|-----------|----------------|
| Suite completa de tests | 125 passed en < 1 s (con fakes) | La lógica de durabilidad no introduce coste algorítmico anómalo a nivel unitario/integración |
| Diseño del camino caliente | 1 lectura/escritura a la capa `stores/` por operación de sesión/tarea; caché en memoria best-effort | Impacto acotado: la caché evita golpear BD en el camino caliente cuando está poblada |
| BD como autoridad | Neon PostgreSQL (tier free) con SQL parametrizado | La latencia adicional es una consulta ligera indexable por PK/estado activo |
| Cobertura de piezas de durabilidad | 88% (informativa) | No es una métrica de rendimiento, pero confirma ejercicio amplio del código nuevo |

## Análisis de impacto (cualitativo)

- **Camino de sesión**: la rehidratación tras reinicio añade un descifrado Fernet + una lectura a
  `session_repository`. Ocurre una vez por sesión reconstruida (no en cada petición, gracias a la
  caché). Impacto esperado: bajo.
- **Camino de tarea**: `/task/{id}` lee caché→BD; `/trigger` hace un check de unicidad contra BD.
  Consultas ligeras; sin joins costosos.
- **Memoria (256 MB)**: la durabilidad no añade estructuras en memoria significativas (la caché
  best-effort ya existía como `TaskManager`/`SessionStore`). Vigilar tras el deploy real.

## Conclusión

- El impacto de rendimiento de la durabilidad es **cualitativamente bajo y acotado por diseño**, pero
  **no se ha validado bajo carga** por falta de umbral NFR2 y de entorno de carga a coste 0 €.
- Verdict de NFR2: **Unverified (diferido)** — consistente con build-and-test. Ver `nfr-validation-matrix.md`.
