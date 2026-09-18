# Instrucciones de Test de Rendimiento — Backend Security Hardening

## Aplicabilidad

**No aplica en este intent.** El scope `security-patch` (estrategia Minimal) no
introduce requisitos no funcionales de rendimiento: `nfr-requirements/` detalla
NFR de seguridad, compatibilidad, coste y testabilidad, pero **ningún target de
latencia, throughput o carga**. Las cinco correcciones no cambian rutas
calientes de forma medible:

- FR6 añade una comprobación `price <= 0` O(1) antes de una llamada de red ya
  existente.
- FR9 sustituye un ternario por una comparación de igual coste.
- FR7 es solo documentación; FR8 elimina una variable de entorno; FR18 no
  cambia código.

## Verdicto

Sin target de rendimiento en el inventario de calidad → una única fila `N/A` en
la matriz de verificación de targets del resumen. No se ejecutan pruebas de
carga (coste 0 €; sin infraestructura de perf).
