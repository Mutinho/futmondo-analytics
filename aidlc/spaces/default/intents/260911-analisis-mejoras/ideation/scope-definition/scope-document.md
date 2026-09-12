# Documento de Alcance — Análisis y Plan de Mejoras de futmondo-analytics

## Objetivo del alcance

Auditar de forma transversal el proyecto futmondo-analytics (arquitectura, código e infraestructura) y producir un plan priorizado de mejoras y puntos críticos-débiles, para abordar en futuros intents. El objetivo de fondo que ordena las prioridades es dejar la base lista para crecer con seguridad reduciendo deuda técnica. [intent-statement]

## Dentro del alcance (in-scope)

El análisis cubre cinco ejes: [Q1]

1. **Arquitectura y estructura de código** — frontend Angular, backend FastAPI, límites entre capas, acoplamiento y cohesión. [Q1]
2. **Seguridad** — autenticación (JWT, cookies HttpOnly), gestión de la sesión Futmondo por usuario, manejo de credenciales y secretos, exposición de datos. [Q1]
3. **Fiabilidad y robustez** — la sincronización asíncrona de 11 pasos, manejo de errores, reintentos, y la fragilidad de las integraciones externas (API Futmondo, API Sofascore vía `curl_cffi`). [Q1]
4. **Rendimiento y coste** — latencia de la sync, llamadas a APIs externas, consumo de recursos, manteniéndose dentro de tiers gratuitos. [Q1]
5. **Calidad y prácticas de ingeniería** — cobertura de tests (frontend y backend), CI/CD, linters, tipado y documentación. [Q1]

## Fuera del alcance (out-of-scope)

- Implementar cualquier mejora: todo cambio de código se abordará en futuros intents independientes. [Q2] [intent-statement]
- El diseño detallado de cada mejora (se hará en el intent de cada una). [Q2]
- El despliegue de cambios. [Q2]

Nota: la experiencia de usuario (UX) y los aspectos de protección de datos NO se rediseñan ni se dictaminan en este trabajo, pero PUEDEN señalarse como puntos débiles en el backlog si el análisis los detecta. [Q2]

## Restricciones transversales

- Mantener el stack actual (Angular + FastAPI + Neon + Fly.io); sin reescrituras grandes. [intent-statement]
- **Coste 0 €**: solo mejoras sostenibles en tiers gratuitos; descartar cualquier gasto recurrente. [intent-statement] [memory:M1]

## Marco de priorización

Cada mejora del backlog se clasifica por **severidad** como eje principal, con **esfuerzo/retorno** como desempate dentro de cada nivel: [Q3]

- **Crítico** — riesgo real de rotura en producción, de seguridad o de pérdida de datos. [Q3]
- **Importante** — deuda técnica que frena el crecimiento o la mantenibilidad. [Q3]
- **Opcional** — mejora deseable de bajo impacto. [Q3]

Dentro de un mismo nivel, se prioriza primero lo que ofrece mejor relación esfuerzo/retorno (quick wins). [Q3]

## Mínimo entregable con valor

El backlog priorizado de mejoras es el entregable mínimo imprescindible. El mapa de arquitectura actual es soporte del análisis y se produce igualmente, pero si hubiera que recortar, el backlog priorizado tiene prioridad. [Q4]

## Assumptions & Open Questions

None.
