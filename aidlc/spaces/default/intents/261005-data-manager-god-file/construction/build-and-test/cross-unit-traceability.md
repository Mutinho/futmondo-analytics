# Cross-Unit Traceability — Build and Test gate (`data_manager_v2`)

Gate de cobertura de nivel de etapa (no la frontera de fase). Enumera cada `FR`
y `NFR` de `requirements.md` y verifica cobertura `OK` con target existente en
`construction/code-generation/traceability.json` (zero-Unit stage-level; no hay
user-stories en scope `refactor`, así que no hay ACs de 3 segmentos que
enumerar).

## Veredicto: PASS

Todos los FR y NFR enumerados están cubiertos con `OK` y target existente.

## Cobertura por ID

| ID | Fuente | Estado | Owning stage/Unit | Target (existe) |
|---|---|---|---|---|
| FR1.1 | requirements.md | OK | code-generation (stage-level) | `data_manager/players/application/players.py` |
| FR1.2 | requirements.md | OK | code-generation | `data_manager_v2.py` (57 métodos) |
| FR1.3 | requirements.md | OK | code-generation | `data_manager/` (14 módulos disjuntos = inventario del plan) |
| FR1.4 | requirements.md | OK | code-generation | `data_manager/match_odds/infrastructure/match_odds_adapter.py` |
| FR2.1 | requirements.md | OK | code-generation | `tests/test_data_manager_players_characterization.py` |
| FR2.2 | requirements.md | OK | code-generation | `tests/test_data_manager_teams_standings_characterization.py` |
| FR2.3 | requirements.md | OK | code-generation | `conftest.py` (fakes) |
| FR3.1 | requirements.md | OK | code-generation | `tests/test_data_manager_clauses_dm_characterization.py` |
| FR3.2 | requirements.md | OK | code-generation | `data_manager/punishments_bonuses/infrastructure/punishments_bonuses_adapter.py` |
| FR3.3 | requirements.md | OK | code-generation | `data_manager/players/infrastructure/players_adapter.py` |
| FR4.1 | requirements.md | OK | code-generation | `data_sync_service.py` (consumidor intacto) |
| FR4.2 | requirements.md | OK | code-generation | `data_manager_v2.py` (SQL-en-router intacto) |
| FR5.1 | requirements.md | OK | code-generation | `code-generation-plan.md` (inventario cerrado en Plan Approval) |
| NFR1 | requirements.md | OK | build-and-test | `tests/test_data_manager_schema_lifecycle_characterization.py` + suite verde |
| NFR2 | requirements.md | OK | build-and-test | `pytest.ini` (piso 27 sostenido) |
| NFR3 | requirements.md | OK | code-generation | `requirements.txt` (sin deps de pago) |
| NFR4 | requirements.md | OK | code-generation | `ruff.toml` (formateo sólo nuevos) |
| NFR5 | requirements.md | OK | code-generation | `data_manager/transactions/infrastructure/transactions_adapter.py` |
| NFR6 | requirements.md | OK | code-generation | `tests/test_data_manager_transactions_characterization.py` |

Nota FR1.3 (una responsabilidad por módulo en orden de acoplamiento): no es una
fila literal en `traceability.json` pero su cumplimiento es el **inventario de
14 módulos disjuntos** del plan aprobado (cubre los 57 métodos) y la estructura
`data_manager/<resp>/` en disco; se marca OK contra esos artefactos existentes.

## Elementos sin cubrir

Ninguno.
