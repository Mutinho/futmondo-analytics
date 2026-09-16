# Performance Validation Questions — Durabilidad del estado

> Etapa Performance Validation (Operation). NFR2 (rendimiento) no tiene umbral numérico definido y no
> hay entorno de carga a coste 0 €. Se documenta el plan y el análisis cualitativo; la validación bajo
> carga formal queda diferida. No se abren preguntas nuevas: el contexto está resuelto por decisiones
> previas (NFR2 sin umbral, coste 0 €, sin staging).

## Contexto resuelto (no requiere pregunta)

- **NFR2 (rendimiento)**: "sin degradación perceptible del camino de sesión", **sin umbral numérico**
  (decisión de requirements: "se validará por medición"). No hay p50/p95/p99 objetivo definido.
- **NFR (escalabilidad)**: `min=max=1` hoy; NFR5 pide no asumir instancia única en el diseño (ya
  cubierto: BD autoridad). Sin objetivo de throughput/concurrencia numérico.
- **Entorno de carga**: no hay staging separado ni herramienta de carga a coste 0 €; ejecutar carga
  real contra producción (una sola máquina 256 MB) no es apropiado ni gratuito.
- **Evidencia disponible**: la suite de 125 tests corre en < 1 s con fakes → la lógica de durabilidad
  no introduce coste algorítmico anómalo a nivel unitario/integración. El impacto en el camino real es
  acotado por diseño (1 lectura/escritura a `stores/`, caché best-effort).
- **Estado consistente con build-and-test**: NFR2 quedó `Unverified` (diferido). Esta etapa confirma
  ese estado y documenta el plan; no fabrica métricas de carga.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
