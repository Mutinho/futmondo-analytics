# Decisiones de Stack Tecnológico — Plan de Mejoras de futmondo-analytics


> En este intent de análisis NO se selecciona un stack nuevo: la decisión es
> MANTENER el stack actual (constraint del intent-statement). Este documento lo
> registra explícitamente con su justificación. [requirements] [technology-stack] [memory:M1]

## Decisión: mantener el stack actual

| Capa | Tecnología (se mantiene) | Justificación |
|------|--------------------------|---------------|
| Frontend | Angular 22 + Material 22 (PWA) | Ya en producción; sin reescrituras grandes (constraint). |
| Backend | FastAPI + Python 3.12 (PyJWT) | Ya en producción; ecosistema conocido por el mantenedor. |
| Base de datos | Neon PostgreSQL (free, Frankfurt) | Serverless con tier gratuito; se consolida como único backend (FR14). |
| Integraciones | API Futmondo (requests), API Sofascore (curl_cffi) | Necesarias para el dominio; su fragilidad se mitiga (FR2/FR4). |
| Despliegue | Fly.io (free allowance) + GitHub Actions (free) | Tier gratuito; se endurece el pipeline (FR17). |
| Auth | JWT (access en memoria + refresh HttpOnly) | Postura endurecida ya presente; se mantiene y refuerza (NFR2). |

## Cambios de stack propuestos por el plan

- **Ninguno de fondo.** El plan poda ramas muertas (SQLite/Turso) y residuos de
  plataformas anteriores (Railway/nixpacks) para dejar Neon como único backend
  (FR14), pero NO introduce tecnologías nuevas ni de pago. [requirements] [memory:M1]

## Restricción de coste

- **Coste 0 €**: toda decisión de stack o infraestructura debe sostenerse en tiers
  gratuitos. Se descarta cualquier servicio con gasto recurrente (Redis gestionado,
  Vault, plataformas de observabilidad de pago). [memory:M1]

## Assumptions & Open Questions

None.
