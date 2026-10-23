# Load Test Plan — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

**NO-APLICA load testing.** F2 es UI cliente; no hay endpoints ni throughput de servidor que cargar (el backend no cambia). Los NFR de performance son de **render**: NFR4.1 scroll fluido (objetivo 60 fps) y feedback de carga <100 ms. Se validan por **observación en el iPhone 13 Pro** (opcionalmente con el FPS gauge de Instruments, gratuito), no con un generador de carga.

| Objetivo | Método | Herramienta |
|----------|--------|-------------|
| Scroll fluido de cards (NFR4.1) | observación al hacer scroll en Presupuesto/detalle | Observación / Instruments |
| Feedback <100 ms al cambiar de campeonato/abrir detalle | observación del spinner inmediato | Observación |

## Assumptions & Open Questions

None.
