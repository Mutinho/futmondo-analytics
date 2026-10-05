# Performance Test Instructions — NO APLICA (Minimal / refactor)

## Decisión

El scope es **refactor** → estrategia **Minimal**, y los requisitos
(`requirements.md`) **no definen ningún target de rendimiento** (NFR1–NFR6 son
equivalencia verificable, cobertura, coste 0 €, higiene de diff, idioma,
seguridad de credenciales). Por tanto no hay carga, latencia ni throughput que
validar.

## Por qué no aplica aquí

- Una descomposición DDD de equivalencia estricta **no cambia el perfil de
  rendimiento**: el SQL se mueve **verbatim** al adapter (misma consulta, mismo
  plan), la fachada sólo delega. No se introduce indirección costosa en caliente
  (la inyección del adapter es construcción de objeto, no por llamada crítica).
- No existe stage posterior `performance-validation` programado en este scope
  `refactor`, así que no hay target diferible: simplemente no hay target de
  rendimiento que medir.

## Owning stage

Ninguno. Si un intent futuro introdujera un target de rendimiento, se mediría en
`performance-validation` (fase Operation) con herramientas gratuitas del stack
(`fly logs`, healthcheck), nunca servicios de pago (ver
`operation-fly-stack.md`).
