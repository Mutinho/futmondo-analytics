# Logical Components — u2-integrations (Integraciones)

Vista lógica de dónde aplican los patrones NFR de U2: fronteras de componente,
dominios de fallo y radio de impacto. Puente entre el diseño NFR y la etapa de
Infrastructure Design. U2 no añade infraestructura; sólo endurece componentes de
código existentes tras una capa/función estrecha testeable.

Consume: `functional-spec.md`, todos los `*-design.md` de esta etapa.
Perspectivas inline: arquitecto + plataforma.

## Componentes lógicos y patrones NFR aplicados

| Componente | Tipo | Patrón NFR aplicado | Dominio de fallo |
|---|---|---|---|
| `IntegrationErrors` | módulo de tipos (U1, nuevo) | codifica recuperable/fatal (BR2.1); sin credenciales (NFR3.1) | Ninguno (módulo puro de tipos) |
| `FutmondoClient` | cliente de integración | excepción tipada (BR1.1), timeout ~5s/~30s (NFR-perf.1), sin credenciales en excepción/log (NFR3.1/3.2) | Aísla el fallo de Futmondo tras la excepción tipada |
| `SofascoreClient` | cliente de integración | `IntegrationBanError` fatal en 403 (BR1.2), timeout, throttle preventivo (heredado) | Aísla el fallo/baneo de Sofascore |
| `SyncService` (punto de captura) | orquestador (mod., no ampliado) | dos ramas `except` (BR2.2), elevación en escritura (BR2.3), traducción a `DEGRADED`/fatal, log estructurado (NFR1) | **Radio de impacto principal**: decide continuar (degradar) o abortar (fatal) |
| Punto de escritura `team_prizes` | operación de persistencia (endurecida) | reemplazo transaccional atómico (NFR2.1) | Todo-o-nada: un fallo no deja estado mixto |
| `SyncStepStatus` | helper existente (reuso) | superficie de `DEGRADED` (NFR2.2) | Ninguno (sólo registra estado de paso) |
| `DbConnection` | capa de conexión (mod.) | transacción/rollback limpio (fatal sin corromper) | Límite de integridad transaccional |

## Dominios de fallo y radio de impacto

- **Fallo de un proveedor externo** (timeout / no parseable): contenido en el
  paso; degrada (`DEGRADED`) y el sync continúa. Radio: un paso.
- **Baneo de Sofascore** (403, fatal): aborta el paso sofascore; los pasos
  independientes continúan; los dependientes degradan. Radio: paso sofascore +
  dependientes directos.
- **Fallo en punto de escritura** (`team_prizes`): la transacción atómica limita
  el radio a "sin cambio" (rollback); nunca corrupción parcial. Radio: contenido
  por la transacción.

## Aislamiento (adaptado a Fly.io + coste 0 €)

- El aislamiento es **a nivel de código** (capa/función estrecha testeable +
  excepción tipada), no de infraestructura: no se añaden servicios, colas ni
  particiones. Coherente con "no ampliar los god-files" y coste 0 €.
- **Bulkhead / aislamiento por proceso / thread-pool por dependencia** →
  NO-APLICA (topología fija `min=max=1`; el aislamiento lógico por excepción
  tipada cubre la necesidad del alcance de U2).

## Puente a Infrastructure Design

- U2 **no requiere cambios de infraestructura**: la etapa de Infrastructure
  Design lo reflejará como "sin cambio de topología" (dos apps Fly.io, Neon,
  crons one-shot). Los patrones de este intent viven en el código, no en la
  infra.

## Assumptions & Open Questions

None.
