# Cross-Unit Traceability — Build and Test (sync god-file refactor)

Puerta de cobertura a nivel de etapa (no el límite de fase Construction).
Enumera cada `FR`/`NFR` de `requirements.md` y verifica su cobertura en la
`traceability.json` de code-generation (no hay user stories `AC` — refactor sin
esa etapa). **Contexto de alcance**: esta pasada de Construction extrajo SOLO el
dominio piloto `match_odds`; los 9 dominios restantes se extraen en pasadas
posteriores. Por eso varios requisitos están **cubiertos parcialmente** (patrón
demostrado en el piloto) y su cobertura completa se completará por dominio.

## Verdicto

**PASS con alcance parcial declarado.** El patrón de descomposición está
implementado y verificado de extremo a extremo en el dominio piloto; ningún
requisito está incumplido. Los requisitos que aplican a los 9 dominios restantes
quedan **pendientes de pasadas posteriores** (no es un fallo de esta pasada, es el
alcance secuenciado aprobado en el gate de Plan Approval).

## Cobertura por requisito

| ID | Estado | Cubierto por | Notas |
|----|--------|--------------|-------|
| FR1.1 | OK (piloto) | `data_sync_service.py` | Superficie pública preservada; `sync_match_odds` sigue con misma firma/import. Completo por definición (la clase y los 10 `sync_*` intactos). |
| FR1.2 | OK (piloto) | `data_sync_service.py` | Facade delgado demostrado en `sync_match_odds`; se replica por dominio. |
| FR1.3 / FR1.3.1 | OK | (inventario de imports) | Inventario hecho; sin símbolo interno movido consumido externamente → no hizo falta shim. Se re-evalúa por dominio. |
| FR2.1 | OK (piloto) | `sync/match_odds/domain/ports.py`, `orchestrator.py` | Layering DDD por dominio demostrado (forma lightweight). Pendiente replicar en 9 dominios. |
| FR2.2 | OK | `sync_all()` en `data_sync_service.py` | Coordinador intacto; orden y clave `match_odds` preservados. |
| FR2.3 | OK | `prizes/` (referencia) + piloto | Patrón `sync_prizes` replicado en el piloto. |
| FR3.1 / FR3.2 | OK (piloto) | `sync/match_odds/infrastructure/match_odds_adapter.py` | SQL tras port/adapter, `data_manager_v2.py` intacto. Pendiente por dominio. |
| FR4.1 | OK (piloto) | `tests/test_sync_match_odds_characterization.py` | Characterization-first aplicado al piloto (7 tests verdes pre/post). |
| FR4.2 | OK | proceso | Trabajo incremental una-unidad-por-dominio en marcha (piloto completado). |
| FR4.3 | Parcial | tests existentes + piloto | `prizes` + flujos degradados ya caracterizados; `match_odds` caracterizado; 8 dominios restantes pendientes de sus pasadas. |
| FR5.1 / FR5.1.1 / FR5.2 | OK (piloto) | `orchestrator.py` + caracterización | Payload, claves literales y orden verificados en verde para `match_odds` y `sync_all()`. |
| FR5.3 | OK (piloto) | `orchestrator.py` | Manejo de errores preservado byte-a-byte (verificado por `git diff` en review). |
| FR5.4 | OK | `prizes/team_prizes_writer.py` | Escritura atómica set-replacement intacta (no tocada; sigue como patrón de referencia). |
| NFR1 | OK | — | Sin dependencias nuevas; coste 0 €. |
| NFR2 | OK (medido) | `pytest.ini` | Piso `--cov-fail-under=27` en verde (34.56%); no relajado. |
| NFR3 | OK (medido) | `ruff check` + git diff | God-files no ampliados; `ruff check` limpio en ficheros nuevos; sin format masivo. |
| NFR4 | OK | ficheros nuevos | Identificadores/docstrings/comentarios en inglés. |

## Elementos no cubiertos

Ninguno **incumplido**. Cobertura de dominio pendiente (fuera del alcance de esta
pasada, por diseño): la extracción completa de los 9 dominios restantes
(`clauses`, `transactions`, `punishments_bonuses`, `dream_teams`, `rosters`,
`round_rankings`, `player_performance`, `players_full`; `prizes` ya extraído) se
aborda en pasadas posteriores repitiendo el ciclo congelar → extraer → verde.
