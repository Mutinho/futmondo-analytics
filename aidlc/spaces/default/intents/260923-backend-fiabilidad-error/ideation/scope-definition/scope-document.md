# Scope Document — Fiabilidad backend (FR3.2 + FR4)

## Alcance (in scope)

Las dos patas completas del intent, como una unidad cohesiva de entrega: [Q1]

### FR3.2 — Manejo de errores (primera oleada)

- Reducir/endurecer las capturas amplias (`except Exception` / bare-except) de:
  **arranque (`main.py`)**, **migraciones (`scripts/migrate_*`)** y
  **`db_connection.py`**, distinguiendo error recuperable de fatal. [desc][Q1]
- Definir e implementar una **taxonomía recuperable/fatal** (recuperable →
  degradado y continúa; fatal → aborta limpio sin datos a medias). [Q3]

### FR4 — Contratos y robustez de integraciones externas

- **`futmondo_client.py` deja de tragar excepciones**: pasa a excepciones
  tipadas por modo de fallo, propagadas (extendiendo el patrón
  `SofascoreIPBanError` ya probado en FR2.1). [Q1][Q2]
- **Detección de baneo/entrada fallida reflejada en el estado**, sin corromper
  datos: reusando/extendiendo `sync_step_status.py` (`StepStatus.DEGRADED`). [Q1][Q2]
- **Documentación de contratos y modos de fallo** esperados de Sofascore (API no
  oficial, baneo IP) y Futmondo (endpoints heterogéneos). [desc][Q2]

## Fuera de alcance (out of scope) — deuda registrada

Exclusiones explícitas para mantener el intent acotado, sin ampliar los
god-files: [Q6][memory:M1]

1. Las **29 capturas completas de `data_sync_service.py`**, salvo puntos de
   corrupción de datos concretos. [Q6]
2. El **resto de broad-except del backend** fuera de la primera oleada. [Q6]
3. La **poda de configuración muerta** (Turso/SQLite, `nixpacks.toml`, etc.) →
   Intent 2. [Q6]
4. La **descomposición de god-files** → Intent 3. [Q6]

## Secuenciación

**Dependencia primero** (capa de errores → clientes → estado), priorizando
dentro de FR4 lo relativo a la corrupción de datos. FR3.2 (capa de errores)
habilita FR4. La secuencia fina de Bolts la fija delivery-planning. [Q3][Q4]

## Restricciones

Sin plazos duros; coste 0 € (tiers gratuitos) es la única restricción dura;
stack fijo; gate CI bloqueante; sin reescrituras grandes; no ampliar god-files. [Q5][desc][memory:M1]

## Assumptions & Open Questions

None.
