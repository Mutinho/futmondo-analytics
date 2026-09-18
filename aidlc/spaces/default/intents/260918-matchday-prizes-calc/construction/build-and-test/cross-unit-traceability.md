# Cross-Unit Traceability — Build and Test (matchday-prizes-calc)

Intent de una sola unidad (U1). No hay integración entre unidades que trazar.

| Unidad | Requisitos | Implementación | Tests | Estado |
|---|---|---|---|---|
| U1 matchday-prizes-calc | FR1–FR3, NFR1–NFR5 | `app/services/prizes/calculator.py`, `data_sync_service.py` | `test_prizes_characterization.py`, `test_prizes_calculator.py` | Verde (150 passed) |

Cobertura de requisitos verificada end-to-end:
- FR1 (reparto ante empates) → BR3.1/BR3.2 → test 2 y 3 empatados (incl. jornada 5).
- FR2 (elegibilidad + premio por posición) → BR2.1/BR2.2 → tests sin empate y `users_to_rank`.
- FR3 (gating + retroactividad) → BR1.1/BR1.2 + orquestador → tests gating y caracterización.
- NFR1/NFR3 (caracterización coste 0 €) → red de caracterización en verde antes del cambio.
- NFR2 (no regresión) → suite completa 150 passed.
- NFR4 (no engordar god-file) → cálculo en `services/prizes/`, `sync_prizes` −10 líneas netas.
- NFR5 (gate CI) → gitleaks + pytest + ng test bloqueantes en PR.
