# Load Test Plan — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

NO-APLICA el load testing clásico: la capa de diseño es UI cliente, sin endpoints ni throughput de servidor que cargar. Los NFR de performance son de **render** (NFR4.1 60 fps objetivo, NFR4.2 feedback de loading <100 ms), validables por observación en el iPhone 13 Pro, no con un generador de carga.

## Plan de validación (adaptado, coste 0 €)

| Objetivo | Método | Herramienta |
|----------|--------|-------------|
| Render fluido del catálogo y el login (NFR4.1) | Scroll y alternar tema/tamaño de texto en el dispositivo; observar jank | Observación / Instruments (gratuito) |
| Feedback de loading inmediato (NFR4.2) | Pulsar "Iniciar sesión" y comprobar que el spinner aparece <100 ms | Observación en dispositivo |

El backend no cambia; su rendimiento no se re-valida por este intent.

## Assumptions & Open Questions

None.
