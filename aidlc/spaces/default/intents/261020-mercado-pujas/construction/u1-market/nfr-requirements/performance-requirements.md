# Performance Requirements — u1-market

> Unit `u1-market` (kind `ui`). Objetivos de **responsividad de UI**, no SLAs de
> servidor: la pantalla consume contratos backend inalterados y la latencia de
> red depende del backend y de la conexión del dispositivo, fuera del alcance de
> esta Unit. **No existe un NFR de rendimiento de servidor en inception**
> (NFR1–NFR6 no incluyen rendimiento); estos objetivos de responsividad de UI se
> derivan como sub-requisitos de **NFR6** (usabilidad/accesibilidad: una UI
> responsiva es parte de la experiencia operable), con IDs `NFR6.x`.

## Sources

- `.../inception/requirements-analysis/requirements.md` (NFR6 usabilidad/accesibilidad).
- `.../construction/u1-market/functional-design/functional-spec.md` (W1–W7).
- `nfr-requirements-questions.md` (Q1).

## Requisitos

| ID | Requisito | Objetivo (verificable) | Origen |
|---|---|---|---|
| NFR6.1 | Primer frame de estado | Al aparecer la pestaña o cambiar el campeonato, la pantalla muestra el estado `loading` de inmediato (sin pantalla en blanco). | Q1, W1 |
| NFR6.2 | Renderizado de la lista | La lista/banner se muestran en cuanto resuelve `GET /market/today`; una recarga sustituye por completo el contenido (sin estado intermedio ambiguo). | Q1, W1 |
| NFR6.3 | Scroll de la lista | La lista usa `LazyVStack` (render perezoso) para scroll fluido con listas largas de jugadores. | Q1, W3 |
| NFR6.4 | Reordenado | Cambiar el criterio de orden reordena la lista **en memoria**, sin red y de forma instantánea (sin recarga). | Q1, W3 |
| NFR6.5 | Escritura no bloqueante de UI | Durante una escritura (`isWriting`), la UI permanece responsiva (indicador de progreso); sólo se deshabilitan los botones de escritura, no la navegación ni el scroll. | Q1, W4/W5 |
| NFR6.6 | Aislamiento del detalle | Abrir/cargar el sheet de detalle Sofascore no bloquea ni degrada la lista (carga en estado local del sheet). | Q1, W7 |

> Nota: estos `NFR6.x` cubren la dimensión de **responsividad/usabilidad** de
> NFR6; los sub-requisitos de accesibilidad de NFR6 (color, VoiceOver, contraste,
> táctil) se detallan en `frontend-components.md` (functional-design) y se
> resumen en `security-requirements.md`/`tech-stack-decisions.md`.

## Fuera de alcance (justificado)

- **SLAs de latencia de red / throughput de servidor**: dependen del backend
  inalterado y de la conexión; `u1-market` es un cliente `ui`, no un servicio.
  No se fijan percentiles de latencia de API ni rps.
- **Benchmarks de carga**: no aplican a una pantalla cliente de un solo usuario.

## Assumptions & Open Questions

None.
