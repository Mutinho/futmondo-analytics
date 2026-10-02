# Performance Test Instructions — `261001-sync-god-file-resto`

## Aplicabilidad

**No aplica** en este intent. La estrategia es Minimal y no existen requisitos
NFR de rendimiento nuevos: el refactor es de equivalencia funcional estricta, sin
cambio de comportamiento observable ni de rutas calientes. No se definen pruebas
de carga/estrés/soak.

## Alternativa a coste 0 €

Si en el futuro se necesitara validar rendimiento, se haría con herramientas
gratuitas (observación por `fly logs`, healthcheck) sin introducir servicios de
pago; fuera de alcance aquí.
