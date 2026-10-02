# Reverse Engineering Timestamp

- **Fecha**: 2026-10-01
- **Intent**: `261001-sync-god-file-resto`
- **Tipo de escaneo**: FOCUSED SCAN sobre un store STALE (merge focalizado; se
  actualizan las secciones del área sync y se preserva la prosa previa fuera de
  ella). Candidato en staging; publicación por compare-and-swap.
- **Repo**: `futmondo-analytics` (raíz del workspace = codebase).
- **Commit / source fingerprint**: `git:99f43293a185982f12244c566eaee0ba87bc918f`
- **Cobertura**: escaneo profundo acotado al set del snapshot del intent
  (`data_sync_service.py`, `sync/`, `prizes/`, el sync router); el resto queda
  skimmed. La cobertura profunda del store previo (`kind: full`,
  `git:e29abff...`) NO se re-verificó en esta pasada y se **demota** a `shallow`.
  Detalle en la sección `Scan Coverage` del handoff del desarrollador.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 261001-sync-god-file-resto
fingerprint: 99f43293a185982f12244c566eaee0ba87bc918f
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
