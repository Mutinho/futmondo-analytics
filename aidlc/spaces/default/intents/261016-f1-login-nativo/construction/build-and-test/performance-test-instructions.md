# Performance Test Instructions — F1: Login nativo end-to-end

> Fase: construcción (build-and-test). Idioma: castellano; identificadores/código en inglés.

F1 no introduce carga ni latencia nuevas: el ajuste de backend solo cambia de dónde se lee el
refresh token (sin I/O ni queries nuevas); el cliente nativo usa `async/await` no bloqueante y un
refresh coalescido que evita trabajo duplicado. No se definen pruebas de rendimiento formales
(coherente con coste 0 y el alcance de F1); la fluidez del arranque/login se observa en la
validación manual en el iPhone.

## Sources
- [consumes] performance-design de los bolts.

## Assumptions & Open Questions
None.
