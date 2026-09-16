# Security Test Instructions — Optimización del bundle inicial

> Stage 3.6 Build and Test · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield.
> Perspectiva: devsecops (rol de apoyo).

## Superficie de seguridad del cambio

Este refactor es de composición de bundle e imports; NO toca autenticación, autorización, manejo de secretos, validación de entradas ni contratos de red. Por tanto no introduce nueva superficie de ataque.

Puntos revisados:
- **Sin dependencias nuevas** (NFR3): el refactor no añade paquetes, por lo que no amplía la cadena de suministro. `chart.js`/`ng2-charts`/`marked` se conservan en su versión actual; solo cambia cuándo se cargan (BR5.2).
- **`marked` (renderizado de Markdown del chat)**: se mantiene el mismo saneo/lógica que hoy (BR2.3); el refactor no cambia cómo se procesa el Markdown, solo difiere la carga del componente. No hay regresión de saneo.
- **Carga diferida de chunks**: los chunks lazy se sirven desde el mismo origen (build de Angular, mismo `output`), sin nuevas fuentes remotas ni CDNs de terceros.

## Verificación

- Sin secretos hardcodeados en los ficheros tocados (estrategia de preloading, config de arranque, componentes, `angular.json`): revisado, ninguno.
- No se ha modificado el interceptor de auth ni ningún guard; su spec (`auth.interceptor.spec.ts`, 6 tests) sigue verde.
- Señal de seguridad preexistente `NODE_TLS_REJECT_UNAUTHORIZED=0` del build: fuera de alcance de este intent (anotada en reverse-engineering, no la introduce este refactor).

Sin tests de seguridad nuevos (no aplica al cambio; coste 0 €).
