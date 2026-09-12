# Requisitos de Rendimiento — Plan de Mejoras de futmondo-analytics


> Objetivos de rendimiento indicativos y medibles, dimensionados para una escala
> pequeña y estable, dentro del tier gratuito. Derivado de NFR4 de
> `requirements.md`. [requirements] [technology-stack] [memory:M1]

## Objetivos de tiempo de respuesta (API síncrona)

- **NFR4.1** — Los endpoints de lectura del mercado/analítica responden en < 800 ms
  a p95 bajo la carga real esperada (decenas de usuarios, uso esporádico). Medición:
  logs de tiempos o prueba manual; objetivo indicativo, no SLA. [requirements]
- **NFR4.2** — La operación de puja (`/market/bid`) responde en < 1,5 s a p95
  (incluye el proxy a Futmondo, dependiente de terceros). [requirements]

## Operaciones de larga duración (sync)

- **NFR4.3** — La sincronización de 11 pasos es asíncrona (no bloquea la petición
  HTTP); el usuario recibe progreso por polling. El tiempo total de sync no tiene
  un objetivo duro (depende de Futmondo/Sofascore), pero cada paso reporta progreso
  para que no parezca colgado. [requirements] [architecture]

## Uso de recursos (coste 0 €)

- **NFR4.4** — El backend opera dentro de los límites de la máquina Fly del tier
  gratuito (256 MB); el pool de conexiones a Neon (5-20) se mantiene dentro de los
  límites del plan free de Neon. Medición: uso de memoria en Fly; conexiones activas
  en Neon. [requirements] [memory:M1]

## Anti-requisitos

- No se persigue "instantáneo" ni objetivos p99 estrictos: la escala no lo justifica
  y perseguirlos podría empujar fuera del tier gratuito.

## Assumptions & Open Questions

- Los umbrales p95 son indicativos y se ajustarán con medición real; no hay
  compromiso de latencia con usuarios. [assumption]
