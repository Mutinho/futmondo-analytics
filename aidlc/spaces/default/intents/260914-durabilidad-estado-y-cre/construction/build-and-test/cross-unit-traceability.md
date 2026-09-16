# Cross-Unit Traceability — Durabilidad del estado

> Etapa Build and Test (Construction), Step 10 (gate de cobertura cruzada, nivel de etapa). Enumera
> cada FR/NFR de `requirements.md` y verifica que está cubierto con status `OK` en al menos un
> `traceability.json` (stage-level o de unidad) y que su archivo objetivo existe. No hay AC de
> user-stories (etapa `user-stories` fue SKIP en este scope).

## Veredicto: PASS

Todos los requisitos funcionales y no funcionales enumerados están cubiertos `OK` por al menos una
unidad, con archivo objetivo existente. No hay elementos sin cubrir.

## Cobertura por ID

| ID | Cubierto | Unidad | Archivo objetivo | Existe |
|----|----------|--------|------------------|--------|
| FR1.1 | OK | u1-durable-session | `backend/app/stores/session_repository.py` | Sí |
| FR1.2 | OK | u1-durable-session | `backend/app/services/session_service.py` | Sí |
| FR1.3 | OK | u1-durable-session | `backend/app/api/v1/endpoints/_helpers.py` | Sí |
| FR1.4 | OK | u2-durable-sync-tasks | `backend/app/services/task_service.py` | Sí |
| FR1.5 | OK | u2-durable-sync-tasks | `backend/app/stores/task_repository.py` | Sí |
| FR1.6 | OK | u2-durable-sync-tasks | `backend/app/api/v1/endpoints/sync.py` | Sí |
| FR5.1 | OK | u1-durable-session | `backend/app/security/credential_protection.py` | Sí |
| FR5.2 | OK | u1-durable-session | `backend/app/security/credential_protection.py` | Sí |
| NFR1 | OK | u1-durable-session | `backend/app/security/credential_protection.py` | Sí |
| NFR2 | OK (Unverified*) | u1-durable-session | `backend/app/auth/session_store.py` | Sí |
| NFR3 | OK | u1 / u2 | `docs/DEPLOY.md`, `backend/app/stores/task_repository.py` | Sí |
| NFR4 | OK | u1 / u2 | `backend/tests/test_durable_session_characterization.py`, `test_durable_task_characterization.py` | Sí |
| NFR5 | OK | u1 / u2 | `backend/app/stores/session_repository.py`, `backend/app/services/task_service.py` | Sí |
| BR1.1 | OK | u1-durable-session | `backend/app/stores/session_repository.py` | Sí |
| BR1.2 | OK | u1-durable-session | `backend/tests/test_durable_session_service.py` | Sí |
| BR1.3 | OK | u1-durable-session | `backend/app/services/session_service.py` | Sí |
| BR1.4 | OK | u1-durable-session | `backend/tests/test_durable_session_repository.py` | Sí |
| BR1.5 | OK | u1-durable-session | `backend/app/services/session_service.py` | Sí |
| BR1.6 | OK | u1-durable-session | `backend/app/auth/routes.py` | Sí |

\* **NFR2** está trazado a código (`OK` en traceability), pero su *objetivo de rendimiento* no tiene
umbral numérico y no se validó por medición en esta etapa (ver `performance-test-instructions.md`):
se marca `Unverified` en la matriz de verificación de objetivos, como diferido consciente, no como
gap de cobertura de requisito.

## Elementos sin cubrir

Ninguno.

## Notas

- No hay `AC` (etapa `user-stories` fue SKIP en el scope `feature` de este intent).
- No existe `traceability.json` a nivel de etapa (no hubo trabajo zero-Unit); la cobertura proviene
  de los dos `traceability.json` por unidad.
