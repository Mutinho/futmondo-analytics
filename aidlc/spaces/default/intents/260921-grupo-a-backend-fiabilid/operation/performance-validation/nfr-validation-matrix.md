# Matriz de validación de NFRs — Fiabilidad de la sync

> Conversation language: Spanish. En vez de un "target vs actual" de rendimiento
> (NO-APLICA), esta matriz valida las **NFRs reales** del intent (NFR1-NFR5)
> contra la evidencia existente, a coste 0 €. Estado global: **VALIDADO**.

## Matriz NFR (objetivo vs. real)

| NFR | Objetivo | Real / Evidencia | Método | Veredicto |
|---|---|---|---|---|
| NFR1 — Fiabilidad observable | Un fallo parcial no se reporta como éxito | Pasos `prizes`/`phantoms` que fallan quedan `status="degraded"` (no `done`) con `reason` + log | `test_sync_step_status.py`, `test_sync_degraded_steps.py` (9 verde); `fly logs` (`sync step degraded`) | **Cumplido** |
| NFR2 — Mantenibilidad | Código nuevo tras función estrecha; god-files intactos | Helper en módulo `sync_step_status.py`; `git diff` aditivo; `data_sync_service.py`/`data_manager_v2.py` sin tocar | revisión de código + `git diff` | **Cumplido** |
| NFR3 — Testabilidad | Specs `pytest` significativas, sin `assert True` | 16 tests nuevos con aserciones reales (estado, payload, 422/200, propagación) | suite 166 verde | **Cumplido** |
| NFR4 — Coste | Coste 0 € (solo herramientas presentes) | `pytest` en `python:3.12` free; sin servicios de pago | inventario de herramientas | **Cumplido** |
| NFR5 — Seguridad | Validación de `price` reforzada en backend (defensa en profundidad) | Techo `PRICE_SANITY_CAP` → 422 antes de proxyar; cliente no invocado | `test_market_bid_sanity_cap.py` (4 verde) | **Cumplido** |

## NFRs de rendimiento/escalabilidad

- **NO-APLICA**: el intent no define objetivos de latencia, throughput,
  tráfico ni escalado (ver `load-test-plan.md` / `test-results.md`). No hay fila
  de rendimiento que validar; sin regresión observada (suite ~4,2 s).

## Veredicto global

**VALIDADO.** Todas las NFRs aplicables del intent (NFR1-NFR5) se cumplen con
evidencia real. Las NFRs de rendimiento/escalabilidad no aplican y se
documentan como tales, sin inventar objetivos ni infraestructura de medición de
pago.

## Sources

- `inception/requirements-analysis/requirements.md` (NFR1-NFR5),
  `construction/build-and-test/{test-results,build-and-test-summary}.md`,
  `construction/sync-reliability/code-generation/traceability.json`,
  `load-test-plan.md`, `test-results.md`.

## Assumptions & Open Questions

None.
