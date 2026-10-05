# Reverse Engineering Timestamp

## Run Metadata

- **Fecha**: 2026-10-05
- **Intent**: `261005-data-manager-god-file`
- **Tipo de escaneo**: FOCUSED SCAN sobre un store STALE (merge focalizado): se
  actualizan las secciones del área del god-file de acceso a datos
  (`data_manager_v2.py`, `services/`, `api/v1/endpoints/`, `stores/`) y se preserva
  la prosa previa fuera de ella. Candidato en staging; publicación por
  compare-and-swap del conductor (backstop + `codekb-publish`).
- **Repo**: `futmondo-analytics` (raíz del workspace = codebase, repo único sin
  cualificador).
- **Commit / source fingerprint**: `git:993f0cb3c0bdaa8c475e2d5bdfcd43f594e555dc`
- **Cobertura**: escaneo profundo acotado a `data_manager_v2.py` (god-file objetivo,
  3692 líneas / 57 métodos / 148 sentencias SQL), `backend/app/services/`,
  `backend/app/api/v1/endpoints/` (8 routers consumidores + patrón SQL-en-router) y
  `backend/app/stores/` (capa de persistencia estrecha de referencia). La cobertura
  profunda registrada por el store previo (`261002-sync-god-file-8`,
  `git:11d63398...`: `data_sync_service.py`, `sync/`, `prizes/`, el sync router) NO
  se re-verificó en esta pasada y, por regla de merge STALE, se **demota** a
  `shallow`. Hallazgo nuevo de esta pasada: `DataManagerV2` es el último god-file
  original sin descomponer; su superficie pública exacta (constructor `skip_init=True`
  + 57 métodos agrupables en ~14 responsabilidades) es el contrato a preservar, pues
  8 routers + los adapters de las 4 oleadas DDD la envuelven verbatim. Riesgos de
  corrupción (`delete_orphan_players`), broad/bare excepts y `return None`
  silenciosos detallados en `code-quality-assessment.md`. Detalle en la sección
  `Scan Coverage` del handoff del desarrollador.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 261005-data-manager-god-file
fingerprint: 993f0cb3c0bdaa8c475e2d5bdfcd43f594e555dc
analyzed:
  paths:
    - backend/app/services/data_manager_v2.py
    - backend/app/services/
    - backend/app/api/v1/endpoints/
    - backend/app/stores/
  components:
    - data-manager-v2
    - services-layer
    - api-v1-routers
    - stores-layer
shallow:
  paths:
    # prior store deep paths demoted (not re-verified this pass):
    - backend/app/services/data_sync_service.py
    - backend/app/services/sync/
    - backend/app/services/prizes/
    - backend/app/api/v1/endpoints/sync.py
    # plus the prior shallow set + any newly skimmed paths:
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
