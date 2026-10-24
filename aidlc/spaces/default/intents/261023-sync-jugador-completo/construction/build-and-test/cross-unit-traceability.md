# Cross-Unit Traceability — Build and Test gate

Verdict: **PASS**. Todos los `FR`/`NFR` de `requirements.md` quedan cubiertos por
la cadena de diseño y materializados en código/tests existentes. Sin huérfanos.

Zero-Unit: trazabilidad a nivel de stage
(`construction/code-generation/traceability.json`,
`functional-design/traceability.json`).

| ID | Cubierto por | Fichero destino (existe) | Verdict |
|---|---|---|---|
| FR1 / FR1.1 / FR1.2 (extracción + points directo) | BR1.1 → code | `backend/app/services/sync/players_full/orchestrator.py` | OK |
| FR1.3 (normalización NaN) | BR1.2 → code | `orchestrator.py` (`clean_float`) | OK |
| FR1.4 (real_team_id) | BR3.1 → code | `favorites_read.py` | OK |
| FR2 / FR2.1 / FR2.2 (esquema idempotente) | BR2.1/BR2.2 → code | `schema_lifecycle_adapter.py`, `players_adapter.py` | OK |
| FR3 / FR3.1 (equipo/escudo) | BR3.1 → code | `favorites_read.py` (`LALIGA_TEAMS`) | OK |
| FR4 / FR4.1 / FR4.2 (favorites_read + contrato) | BR4.1/BR4.2 → code+tests | `favorites_read.py`, `test_favorites_read_enriched.py` | OK |
| FR5 / FR5.1 (market no se toca) | N/A por diseño (O2) | — | OK |
| NFR1 (contrato) | BR4.2 → tests | `test_favorites_read_enriched.py` | OK |
| NFR2 (characterization-first) | BR5.1 → tests | `test_sync_players_enrichment.py` + suite verde | OK |
| NFR3 (coste 0) | tech-stack | sin dependencias nuevas | OK |
| NFR4 (gate verde) | build-and-test | 463 passed, cobertura 60,82% | OK |
| NFR5 (sin backfill / defaults) | BR5.2 → code+tests | `favorites_read.py`, `test_favorites_read_enriched.py` | OK |
| NFR6 (migración segura) | BR2.1 → tests | `test_schema_players_columns.py` | OK |

## IDs sin cubrir

Ninguno.
