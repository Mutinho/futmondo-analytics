# Cross-Unit Traceability — Build and Test (FR3.2 + FR4)

Gate de cobertura final a nivel de etapa (no es el límite de fase). Enumera cada
`FR`/`NFR` de `requirements.md` y verifica que está cubierto `OK` en al menos una
entrada de trazabilidad de unidad (u1-error-layer / u2-integrations) o por
evidencia de este stage. (user-stories se omitió en este intent → no hay AC de
tres segmentos que enumerar.)

## Verdict: PASS — todos los FR/NFR cubiertos

| ID | Unidad(es) | Estado | Target / evidencia |
|---|---|---|---|
| FR3.2.1 (taxonomía recuperable/fatal) | u1 | OK | `integration_errors.py` (tipo codifica clasificación); `test_integration_errors.py`, `test_error_layer_hardening.py` |
| FR3.2.2 (1ª oleada arranque/migraciones/db_connection) | u1 | OK | `main.py`, `db_connection.py`, `scripts/migrate_to_turso.py` |
| FR3.2.3 (`E722` advisory) | u1 | OK (config) | `backend/ruff.toml` (E722 fuera de `ignore`, advisory) |
| FR4.1 (módulo `IntegrationErrors`) | u1 | OK | `integration_errors.py` (jerarquía raíz común) |
| FR4.2 (`FutmondoClient` tipado) | u2 | OK | `futmondo_client.py::_make_request`; `test_futmondo_client_typed_failures.py` |
| FR4.3 (inventario de llamadores) | u2 | OK | `test_futmondo_client_characterization.py` + `code-summary.md` |
| FR4.4 (detección de baneo en estado) | u1 + u2 | OK | `sofascore_client.py` (u1) + captura en sync (u2); `test_sync_integration_failure_effect.py` |
| FR4.5 (doc contratos/modos de fallo) | u2 | OK | `code-summary.md` (sección de contratos) |
| NFR1 (log estructurado) | u2 | OK | `_log_integration_failure` (clave=valor WARNING/ERROR) |
| NFR2 (no-corrupción) | u2 | OK | `team_prizes_writer.py` (reemplazo atómico); `test_team_prizes_atomic_replacement.py` |
| NFR3 (sin secretos en excepciones) | u1 + u2 | OK | constructor `integration_errors` (u1) + aserción de log (u2) |
| NFR4 (sin regresión) | build-and-test | OK | suite completa 203 passed, 0 failed (`test-results.md`) |
| NFR5 (coste 0 €) | build-and-test / tech-stack | OK | sin dependencias nuevas de pago; venv efímero para repro; GitHub Actions/Fly.io free |

## Elementos sin cubrir

Ninguno.

## Deuda registrada (fuera de alcance, no es hueco de cobertura)

- Migración de contrato de `_make_request` limitada al **núcleo**; los llamadores
  de `roster.py` quedan como deuda documentada (FR4.3 lo permite explícitamente).
- `except: pass` de `data_manager_v2.py` / `photo_service.py` → deuda (Intent 3).
- Asimetría de la señal `--cov` entre `ci.yml` y `verify` → deuda de pipeline diferida.
