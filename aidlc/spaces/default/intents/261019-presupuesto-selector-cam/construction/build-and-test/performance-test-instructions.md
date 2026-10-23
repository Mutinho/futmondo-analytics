# Performance Test Instructions — F2

> Fase: construcción (build-and-test). Idioma: castellano; tokens técnicos verbatim en inglés.

NO-APLICA medición automatizada en WSL. Los NFR de render (NFR4: 60 fps scroll, <100 ms feedback de carga) se validan por **observación en el iPhone 13 Pro** (opcionalmente con el FPS gauge de Instruments, gratuito). Se registra en Performance Validation (Operación). El `BudgetViewModel` fija `loading` síncrono antes del `await` (diseño que habilita el <100 ms).

## Assumptions & Open Questions

None.
