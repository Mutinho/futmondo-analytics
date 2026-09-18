# Cobertura Final Cross-Unit — Backend Security Hardening

> Gate de cobertura a nivel de etapa (no el límite de fase). Enumera cada FR y
> NFR de `requirements.md` y verifica cobertura `OK` en
> `construction/code-generation/traceability.json` (zero-Unit: fichero
> stage-level). No se enumeran AC de user-stories porque esa etapa se saltó
> (scope `security-patch`).

## Veredicto: PASS

Todos los requisitos funcionales del intent tienen cobertura `OK` con fichero de
implementación o test existente. Los NFR de seguridad detallados (`NFR1.x`)
trazan a su FR y están cubiertos por los mismos tests.

## Cobertura por requisito funcional

| ID | Cubierto | Estado | Fichero(s) / target | Fuente de cobertura |
|----|----------|--------|---------------------|---------------------|
| FR6 (FR6.1–6.3) | Sí | OK | `market.py::place_bid`; `test_market_bid_validation.py` | traceability.json |
| FR7 (FR7.1–7.3) | Sí | OK | `main.py` (docs); `test_photos_exposure.py` | traceability.json |
| FR8 (FR8.1–8.2) | Sí | OK | `docker-compose.yml`; `test_tls_verification.py` | traceability.json |
| FR9 (FR9.1–9.3) | Sí | OK | `token_store.py`; `test_auth_characterization.py`, `test_durable_session_characterization.py` | traceability.json |
| FR18 (FR18.1–18.2) | Sí | OK | `test_db_admin_guard.py` (guarda ya correcta en `reset_db.py`) | traceability.json |

## Cobertura por requisito no funcional (inception)

| ID | Tema | Cubierto | Nota |
|----|------|----------|------|
| NFR1 | Seguridad (no regresión) | Sí | Detallado en `NFR1.1`–`NFR1.9`; invariantes verificadas, sin credenciales en claro, sin `JWT_SECRET` default |
| NFR2 | Compatibilidad de stack | Sí | Sin reescrituras; sin ampliar SQL-en-router ni god-files |
| NFR3 | Coste 0 € | Sí | Sin dependencias de pago; venv efímero y Docker gitleaks son gratuitos |
| NFR4 | Gate CI verde | Sí (local) / Diferido (gitleaks del PR) | `pytest` 135 passed local; gitleaks + `ng test` los ejecuta el gate de CI del PR |
| NFR5 | Testabilidad (test-after) | Sí | ≥1 test verificable por FR, camino de error cubierto |

## Elementos sin cubrir

Ninguno. Todos los FR y NFR enumerados están cubiertos.

## Hallazgo elevado (fuera de alcance del intent)

Secreto **preexistente** en el historial de git (detectado por gitleaks;
`auth.py` eliminado, commit de 2025-11-11), ajeno a este patch. No afecta a la
cobertura de los requisitos; se recomienda rotar/purgar como trabajo de
seguridad independiente. Detalle en `test-results.md`.
