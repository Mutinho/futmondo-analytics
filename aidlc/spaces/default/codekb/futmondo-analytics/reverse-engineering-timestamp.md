# Reverse Engineering Timestamp

- **Fecha**: 2026-10-02
- **Intent**: `261002-sync-god-file-8`
- **Tipo de escaneo**: FOCUSED SCAN sobre un store STALE (merge focalizado; se
  actualizan las secciones del área sync y se preserva la prosa previa fuera de
  ella). Candidato en staging; publicación por compare-and-swap del conductor.
- **Repo**: `futmondo-analytics` (raíz del workspace = codebase, repo único sin
  cualificador).
- **Commit / source fingerprint**: `git:11d63398eec619e1957ed772f4e273ff119e70ed`
- **Cobertura**: escaneo profundo acotado a los 4 paths focalizados
  (`data_sync_service.py`, `sync/`, `prizes/`, el sync router); el resto queda
  skimmed. La cobertura profunda registrada por el store previo
  (`261001-sync-god-file-resto`, `git:99f43293...`) NO se re-verificó en esta
  pasada y, por regla de merge STALE, se **demota** a `shallow`. Hallazgo nuevo de
  esta pasada: el patrón DDD objetivo cuenta ya con DOS pilotos probados
  (`match_odds` + `clauses`); `data_sync_service.py` ha reducido a ~77 KB / ~1806
  líneas tras la extracción de `clauses`; quedan 8 dominios inline + la
  uniformización de `sync_prizes`. Detalle en la sección `Scan Coverage` del
  handoff del desarrollador.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 261002-sync-god-file-8
fingerprint: 31543a53d87649e5b9213c62fc6934a17a9c0167
analyzed:
  paths:
    - backend/app/services/data_sync_service.py
    - backend/app/services/sync/
    - backend/app/services/prizes/
    - backend/app/api/v1/endpoints/sync.py
  components:
    - data-sync-service
    - sync-context
    - prizes-context
    - api-v1-routers
shallow:
  paths:
    - backend/app/services/analytics/
    - backend/app/services/assistant_service.py
    - backend/app/services/analytics_service.py
    - backend/app/services/data_manager_v2.py
    - backend/app/services/futmondo_client.py
    - backend/app/services/sofascore_client.py
    - backend/app/services/photo_service.py
    - backend/app/services/task_service.py
    - backend/app/services/session_service.py
    - backend/app/services/integration_errors.py
    - backend/app/services/sync_step_status.py
    - backend/app/services/
    - backend/app/
    - backend/app/api/
    - backend/pytest.ini
    - backend/ruff.toml
    - backend/requirements.txt
    - backend/conftest.py
    - backend/tests/
    - backend/scripts/
    - angular-app/src/app/
    - angular-app/package.json
    - .github/workflows/
    - proxy/
    - docs/
    - cron/
    - scripts/
    - README.md
```
