# Requisitos de Fiabilidad — Plan de Mejoras de futmondo-analytics


> Objetivos de fiabilidad realistas para infraestructura de coste 0 € (Fly.io free
> allowance, una máquina 256 MB; Neon free) y un mantenedor único. Sin SLA con
> usuarios. El foco es la durabilidad del estado y los datos, no un uptime alto.
> Derivado de NFR1 de `requirements.md`. [requirements] [technology-stack] [memory:M1]

## Disponibilidad (best-effort)

- **NFR1.1** — Objetivo de disponibilidad best-effort ~99% mensual, SIN multi-AZ
  ni failover automático (incompatibles con coste 0 €). Es un objetivo indicativo,
  no un SLA. Medición: revisión de logs/healthchecks de Fly. [requirements] [memory:M1]

## Durabilidad de estado y datos (foco principal)

- **NFR1.2** — El estado de una tarea de sync sobrevive a un reinicio de la máquina
  Fly: tras reinicio, la tarea puede consultarse y refleja su último estado conocido
  (no desaparece). Verificación: simular reinicio con un sync en curso. Origen: FR1. [requirements]
- **NFR1.3** — Tras un reinicio, la sesión Futmondo se reconstruye o el usuario
  recibe una acción clara de re-login, en lugar de un 403 opaco. Origen: FR1. [requirements]
- **NFR1.4** — El reemplazo de la caché de Sofascore es atómico: un fallo a mitad
  de repoblado deja intacta la caché anterior (nunca vacía por fallo parcial).
  Verificación: inyectar fallo a mitad y comprobar que la caché previa persiste.
  Origen: FR2. [requirements]
- **NFR1.5** — Los datos productivos residen en Neon PostgreSQL; se documenta la
  política de backup/recuperación disponible en el tier gratuito (RPO/RTO
  best-effort, sin coste añadido). [requirements] [memory:M1]

## Tolerancia a fallos de integraciones

- **NFR1.6** — Un fallo o baneo temporal de Sofascore no corrompe datos (ver
  NFR1.4) y se refleja en el estado de la tarea; los pasos "non-critical" de la
  sync reportan su fallo de forma visible en vez de ocultarlo. Origen: FR3, FR4. [requirements]

## Objetivos de recuperación (indicativos)

| Objetivo | Valor indicativo | Nota |
|----------|------------------|------|
| RTO (reinicio de máquina) | minutos (arranque de la app Fly) | best-effort |
| RPO (datos en Neon) | según backup del tier gratuito | documentar |
| Pérdida de estado de sync | 0 (tras FR1) | objetivo del plan |

## Assumptions & Open Questions

- Se asume que ~99% best-effort es aceptable para el uso actual (grupo de amigos);
  no hay compromiso contractual de uptime. [assumption]
