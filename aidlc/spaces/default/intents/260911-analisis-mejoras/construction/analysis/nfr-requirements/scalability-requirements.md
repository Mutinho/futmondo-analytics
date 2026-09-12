# Requisitos de Escalabilidad — Plan de Mejoras de futmondo-analytics


> Escala pequeña y estable (grupo de amigos, decenas de usuarios). El requisito de
> escalabilidad es esencialmente "seguir cabiendo en el tier gratuito" y documentar
> el umbral que obligaría a reconsiderar. Derivado de NFR4 de `requirements.md`.
> [requirements] [technology-stack] [memory:M1]

## Modelo de carga y crecimiento

- **NFR4.5** — Carga esperada: decenas de usuarios concurrentes como máximo, uso
  esporádico (picos alrededor de jornadas de mercado). Crecimiento: plano/lento.
  No hay objetivo de crecimiento agresivo. [requirements]

## Capacidad dentro del tier gratuito

| Dimensión | Situación actual | Umbral de reconsideración |
|-----------|------------------|---------------------------|
| Máquinas Fly | 1 (256 MB, min_machines_running=1) | uso sostenido de memoria cerca del límite de 256 MB |
| Conexiones Neon | pool 5-20 | acercarse al límite de conexiones del plan free de Neon |
| Almacenamiento Neon | datos de campeonato | acercarse al límite de almacenamiento free de Neon |
| Cómputo GitHub Actions | 4 workflows | acercarse al límite de minutos gratuitos |

- **NFR4.6** — Se documentan estos umbrales para que un crecimiento inesperado se
  detecte antes de incurrir en coste. La estrategia por defecto ante un umbral es
  optimizar (consultas, frecuencia de sync) manteniendo coste 0 €, no escalar de pago. [requirements] [memory:M1]

## Estrategia de escalado

- **NFR4.7** — Escalado vertical/horizontal de pago queda FUERA por la restricción
  de coste 0 €. Ante presión de capacidad, la vía es optimización (ver god files
  FR13, patrón de llamadas FR16) y reducir frecuencia/tamaño de las sync. [requirements]

## Assumptions & Open Questions

- Se asume escala pequeña estable; si el proyecto se abriera a más grupos, este
  documento debería revisarse con datos reales de uso. [assumption]
