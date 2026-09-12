# Intent Backlog — Ejes de Análisis (proto-unidades)

Este backlog enumera los ejes de análisis que la auditoría cubrirá. No son mejoras todavía (esas saldrán como hallazgos priorizados del análisis), sino las áreas de trabajo del propio análisis. El reverse-engineering y las etapas siguientes producirán, dentro de cada eje, los hallazgos concretos con su prioridad crítico/importante/opcional. [Q1] [Q3]

## Ejes de análisis

| ID | Eje | MoSCoW | Descripción | Source |
|----|-----|--------|-------------|--------|
| AX1 | Arquitectura y estructura de código | Must | Mapear arquitectura real (Angular, FastAPI, proxy, cron), límites de capas, acoplamiento, patrones y anti-patrones | [Q1] [Q4] |
| AX2 | Seguridad | Must | Revisar auth (JWT/cookies), sesión Futmondo, manejo de credenciales y secretos, exposición de datos y endpoints | [Q1] |
| AX3 | Fiabilidad y robustez | Must | Analizar la sync async de 11 pasos, manejo de errores/reintentos, y fragilidad de integraciones Futmondo/Sofascore | [Q1] |
| AX4 | Rendimiento y coste | Should | Evaluar latencia de sync, patrón de llamadas a APIs externas, consumo de recursos dentro de tiers gratuitos | [Q1] |
| AX5 | Calidad y prácticas de ingeniería | Must | Revisar tests (frontend/backend), CI/CD, linters, tipado y documentación | [Q1] |

## Orden de prioridad de cobertura del análisis

1. **AX1, AX2, AX3, AX5** (Must) — el núcleo del análisis: arquitectura, seguridad, fiabilidad y calidad. Son los ejes con mayor probabilidad de contener hallazgos críticos o importantes para "crecer con seguridad". [Q4] [intent-statement]
2. **AX4** (Should) — rendimiento y coste; importante pero, dado el tamaño actual y la restricción de coste 0 €, con menor probabilidad de hallazgos críticos que los anteriores. [Q3] [memory:M1]

## Mínimo entregable con valor

El backlog priorizado de hallazgos (resultado de recorrer estos ejes) es el entregable mínimo imprescindible. [Q4]

## Assumptions & Open Questions

None.
