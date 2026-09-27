# Instrucciones de Tests de Integración — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, test strategy **Minimal**. Conversation language: Spanish.

## Aplicabilidad

**N/A en esta oleada.** La estrategia Minimal no genera ficheros de test adicionales (los unit tests los cubre Code Generation), y este refactor **preserva el comportamiento observable** sin crear fronteras de integración nuevas: el endpoint `analytics.py` consume `AnalyticsService` exactamente como antes, y la fachada delega en el adaptador sobre el `DataManagerV2` actual. No hay integración nueva entre servicios que ejercitar.

La equivalencia observable en el límite fachada→adaptador→BD ya queda cubierta por:
- los **11 tests de caracterización** de `backend/tests/test_analytics_service.py` (payload idéntico antes/después, BR1.1), y
- los **tests de contrato del adaptador** (forma de fila de `fetch_all_teams` / `fetch_players_by_ids` contra el fake in-memory, BR1.2).

## Cómo se re-verificaría (si aplicara)

Si una oleada futura introdujera una frontera de integración nueva, sus tests vivirían junto a la suite existente y se ejecutarían con el mismo comando de gate:

```bash
cd backend && python -m pytest --cov=app -q
```

Por ahora, no hay comando de integración específico que ejecutar en esta oleada.
