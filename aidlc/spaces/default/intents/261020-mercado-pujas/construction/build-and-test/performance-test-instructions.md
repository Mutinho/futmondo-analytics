# Performance Test Instructions — F3 Mercado (u1-market)

> Standard strategy no exige tests de performance formales; F3 es un cliente de
> UI de un solo usuario que consume contratos backend inalterados, no un
> servicio con SLAs de carga. Este documento registra las comprobaciones de
> **responsividad de UI** aplicables y marca explícitamente lo que NO aplica.

## Alcance

- **No hay load/stress/soak tests**: `u1-market` no es un servicio; no se mide
  rps ni throughput (el backend es inalterado). Los NFR de rendimiento son de
  **responsividad de UI** (`NFR6.x`), no SLAs de servidor.

## Comprobaciones de responsividad (validadas en dispositivo)

| ID | Comprobación | Método |
|---|---|---|
| NFR6.1 | Primer frame de estado inmediato | Validación visual en dispositivo (iPhone 13 Pro, `xtool dev build`, diferido a dispositivo) |
| NFR6.3 | Scroll fluido con lista larga | Validación visual en dispositivo |
| NFR6.4 | Reordenado instantáneo (en memoria) | Cubierto por `MarketSorterTests` (lógica pura, O(n log n)) |
| NFR6.5 | Escritura no bloquea scroll/navegación | Validación en dispositivo |

## No aplica (justificado)

- Benchmarks de latencia de red / percentiles p95/p99: dependen del backend y de
  la conexión, fuera del alcance de un cliente `ui`.
- Auto-scaling / capacity planning: no hay infraestructura nueva (backend
  inalterado).

## Assumptions & Open Questions

None.
