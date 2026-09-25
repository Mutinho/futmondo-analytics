# Constraint Register — Fiabilidad backend (FR3.2 + FR4)

## Restricciones técnicas

| ID | Restricción | Fuente |
|---|---|---|
| C-T1 | Mantener el stack actual: FastAPI / Python 3.12, Neon PostgreSQL, Fly.io; sin cambios de infraestructura | [desc][Q4][memory:M3] |
| C-T2 | Sin reescrituras grandes; código nuevo tras una capa/función estrecha y testeable | [desc] |
| C-T3 | NO ampliar los god-files (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router | [desc][memory:M1] |
| C-T4 | Reusar `sync_step_status.py` (FR3.1) como punto de anclaje del estado degradado; extensión estrecha permitida | [Q2] |
| C-T5 | Patrón de fallo de integración = excepción tipada por modo de fallo, propagada (extiende `SofascoreIPBanError`); sin `return None` silencioso | [Q1] |
| C-T6 | Sin dependencias de pago; cualquier librería nueva sería OSS y fijada a versión (no se prevé ninguna, stdlib suficiente) | [Q4][memory:M2] |

## Restricciones organizativas

| ID | Restricción | Fuente |
|---|---|---|
| C-O1 | Mantenedor único: decide alcance y aprueba cada gate; sin plazo externo | [Q5] |
| C-O2 | Gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción | [desc] |
| C-O3 | Test-after con specs significativas; characterization-first en zonas brownfield que se endurezcan | [desc] |
| C-O4 | Nunca reformatear en masa (`ruff format`); formatear solo lo nuevo o de forma quirúrgica | [memory:M1] |

## Restricciones regulatorias / de seguridad

| ID | Restricción | Fuente |
|---|---|---|
| C-R1 | Sin marco regulatorio formal (no PCI/HIPAA/SOC2/GDPR formal) | [Q3] |
| C-R2 | Credenciales Futmondo nunca en claro (ni memoria ni BD); control interno afirmado | [Q3] |
| C-R3 | `JWT_SECRET` no-default en arranque; control interno afirmado | [Q3] |
| C-R4 | Specs usan dobles/mocks, nunca credenciales ni tokens reales (gitleaks escanea tests) | [Q3][Q6] |

## Restricciones económicas

| ID | Restricción | Fuente |
|---|---|---|
| C-E1 | Coste 0 € (Neon free, Fly.io free allowance, GitHub Actions free); descartar toda dependencia con gasto recurrente | [desc][memory:M2] |

## Assumptions & Open Questions

None.
