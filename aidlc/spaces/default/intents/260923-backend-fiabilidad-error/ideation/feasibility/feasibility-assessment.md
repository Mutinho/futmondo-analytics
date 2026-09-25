# Feasibility Assessment — Fiabilidad backend (FR3.2 + FR4)

## Viabilidad técnica

**Veredicto: viable, riesgo bajo-medio, sin dependencias nuevas.** El intent es
un endurecimiento aditivo del manejo de errores y de los contratos de
integración sobre un backend FastAPI/Python 3.12 ya en producción; no requiere
reescrituras ni cambios de infraestructura. [desc][Q4]

### Patrón de detección de fallo (FR4)

Existe un precedente probado que hace el trabajo viable de inmediato:
`sofascore_client.py` ya define `SofascoreIPBanError` y **propaga** el baneo
(HTTP 403) sin tragarlo en el `except` genérico (FR2.1). El enfoque elegido es
**extender ese patrón**: cada modo de fallo esperado (baneo, timeout, respuesta
heterogénea o no parseable) se modela como una excepción tipada que se propaga
hasta el punto que decide degradar o abortar; se elimina el anti-patrón actual
de `futmondo_client.py`, que traga `RequestException`/`Timeout`/`JSONDecodeError`
y devuelve `None` de forma silenciosa. [Q1] El *tipo* de excepción ES la
clasificación recuperable/fatal, coherente con la semántica fijada en
intent-capture. [Q1]

### Punto de anclaje del estado (FR3.2 → FR4)

FR3.1 ya introdujo `sync_step_status.py` (`StepStatus.DEGRADED`,
`record_degraded_step(...)`, `ProgressSink`) fuera de los god-files. El intent
**reusa y extiende estrechamente** ese helper: un baneo o entrada fallida
capturado en la ruta de sync marca el paso como `degraded`/fallido en el mismo
punto canónico, sin ampliar `data_sync_service.py` ni `data_manager_v2.py`. [Q2][memory:M1]

### Reducción de broad-except (FR3.2)

La primera oleada (arranque `main.py`, migraciones `scripts/migrate_*`,
`db_connection.py`) es viable con la stdlib: sustituir capturas amplias/`pass`
por manejo que distinga recuperable (registrar/degradar) de fatal (propagar y
abortar limpio). `db_connection.py` ya hace `rollback()` + `raise` en sus
transacciones, lo que da una base correcta sobre la que endurecer el resto. [Q7]

## Perspectiva de plataforma (Fly.io + Neon)

Sin impacto de infraestructura: no se tocan `fly.toml`, la topología de apps ni
Neon. Los tests nuevos corren en el gate de CI ya existente (gitleaks + `pytest`
+ `ng test`) sobre GitHub Actions free tier. Sin dependencias de pago; cualquier
librería nueva (no se prevé ninguna) sería OSS y fijada a versión. Coste 0 €
mantenido. [Q4][memory:M2][memory:M3]

## Perspectiva de compliance

Sin marco regulatorio formal aplicable (no PCI/HIPAA/SOC2/GDPR formal): proyecto
personal, single-maintainer. Se mantienen como **restricciones internas** los
controles de seguridad ya afirmados: credenciales Futmondo nunca en claro,
`JWT_SECRET` no-default, gitleaks bloqueante (escanea también los tests). Los
specs de este intent usan dobles/mocks, nunca credenciales ni tokens reales. [Q3]

## Incertidumbre técnica (a resolver en diseño)

1. **Clasificación recuperable/fatal de cada captura existente** en
   arranque/migraciones/`db_connection.py`, sin romper el comportamiento actual. [Q7]
2. **Punto de corte "no corromper datos"**: dónde exactamente en la ruta de sync
   un fallo fatal debe abortar antes de escribir, para no dejar datos a medias
   (enlaza con FR2, ya hecho). [Q7]

Ambas se resuelven en functional-design / nfr; se registran aquí como incógnitas
conocidas, no como bloqueadores. [Q7]

## Assumptions & Open Questions

None.
