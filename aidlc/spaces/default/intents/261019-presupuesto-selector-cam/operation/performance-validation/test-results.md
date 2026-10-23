# Performance Test Results — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Ejecutable (WSL)

- `cd ios && swift build && swift test` → verde (105/0). La lógica (formateo, orden, DTOs, servicios) no introduce costes perceptibles; orden/formato son O(n) sobre listas cortas.

## Render (dispositivo iPhone 13 Pro) — validado por el propietario

Durante el re-trabajo de U2, el propietario instaló y usó la app repetidamente:
- **Scroll de cards** en Presupuesto y detalle: fluido, sin jank perceptible (proxy de 60 fps). ✅
- **Feedback de carga**: el spinner aparece de inmediato al cambiar de campeonato o abrir el detalle (loading síncrono antes del await). ✅
- **Animaciones iOS 26**: zoom transition y entrada escalonada del detalle percibidas suaves. ✅

## Veredicto

- Ejecutable: **Met** (build/tests verdes).
- Render/animaciones (NFR4): **Met por validación en dispositivo** (no medible numéricamente en WSL). Ningún objetivo relajado.

## Assumptions & Open Questions

None.
