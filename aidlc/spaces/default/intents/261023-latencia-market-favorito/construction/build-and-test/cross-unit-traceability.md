# Cross-Unit Traceability — Build and Test gate

Verdict: **PASS**. Todos los `FR`/`NFR` de `requirements.md` están cubiertos a
través de la cadena de diseño y materializados en código/tests existentes. No
hay IDs huérfanos.

Zero-Unit (sin Units): se usa la trazabilidad a nivel de stage
(`construction/code-generation/traceability.json`, `nfr-requirements/traceability.json`,
`functional-design/traceability.json`).

## Cobertura por requisito

| ID | Cubierto por | Fichero destino (existe) | Verdict |
|---|---|---|---|
| FR1 (favorites desde sync) | BR2.1 → code | `backend/app/services/sync_read/favorites_read.py` | OK |
| FR1.1/1.2 | BR2.1 → code + tests | `favorites_read.py`, `test_favorites_read.py` | OK |
| FR1.3 (orden) | BR2.2 → tests | `test_favorites_read.py` (orden asc/desc) | OK |
| FR2 / FR2.1 (market sin llamada viva de catálogo) | BR4.1 → code | `backend/app/api/v1/endpoints/market.py`, `market_read.py` | OK |
| FR2.2 (pujas coherentes) | BR4.2/BR5.1 → code | `market.py` (pujas vivas), `market_read.py` (`available_for_bids`) | OK |
| FR3 / FR3.1 (contrato intacto) | BR6.1 → caracterización | `test_favorites_read_characterization.py` | OK |
| FR4 / FR4.1/4.2 (fallback) | BR3.1/BR3.2 → code | `favorites.py` (sync-miss + log), `market.py` (degradación) | OK |
| FR5 / FR5.1 (capa estrecha) | BR1.1 → code | `backend/app/services/sync_read/` | OK |
| FR5.2 (reutiliza sync) | BR2.1 → code | `favorites_read.py` (lee tablas sincronizadas) | OK |
| NFR1 (<0,5s) | NFR1.1/1.2 | medición en Performance Validation (owning stage) | OK (diferido con dueño) |
| NFR2 (frescura) | BR4.2 → code | `market.py` (pujas vivas) | OK |
| NFR3 (coste 0) | tech-stack | sin dependencias nuevas | OK |
| NFR4 (characterization-first) | tests | `test_favorites_read_characterization.py` + suite verde | OK |
| NFR5 (errores/seguridad) | NFR5.3/5.4 → code+tests | `favorites_read.py`/`market.py`, `test_sync_read_endpoints.py` | OK |
| NFR6 (sin cambio de esquema/contrato) | BR6.1 → caracterización | solo lectura; contrato congelado | OK |

## IDs sin cubrir

Ninguno.
