# Reverse Engineering — Registro de Ejecución

> Registro de cuándo se realizó el reverse-engineering y del alcance analizado.
> El bloque `## Scope of Analysis` es leído por `codekb-scope-diff` en el próximo
> rerun, por lo que refleja lo que este escaneo cubrió realmente.

## Metadatos de ejecución

- **Fecha**: 2026-09-11T12:58:18Z
- **Commit hash**: `dcc4139d6eeb465621bb50b8a83aa7bf8f9ebb0a` (`dcc4139`)
- **Tipo de escaneo**: FULL (primera vez, sin store previo — NO_STORE)
- **Profundidad**: Standard
- **Tipo de proyecto**: Brownfield
- **Repo**: repo único (workspace root), `/home/javi/futmondo-analytics`
- **Intent**: analisis-mejoras
- **Pipeline**: developer (escaneo) → architect (síntesis, este artefacto)

## Alcance y notas

Escaneo FULL que cubrió el repo completo: raíz, `backend/` (config, auth,
services, los 23 endpoints, tests, scripts), `angular-app/` (build, core,
features a nivel de directorio), `proxy/`, `cron/` y `.github/workflows/`. Los
"god files" de `backend/app/services/` se conocen por interfaz y llamadas (skim),
y las 17 features Angular se inventariaron a nivel de directorio/fichero. Estos
matices se reflejan en `shallow.paths` del bloque siguiente. La huella
(`fingerprint`) se deja como `unknown`: la acuña el conductor.

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: analisis-mejoras
fingerprint: e754d1ca9d5677d9ec0876b91b089ae27858f272
analyzed:
  paths:
    - ./
    - backend/
    - backend/app/
    - backend/app/core/
    - backend/app/auth/
    - backend/app/services/
    - backend/app/api/v1/endpoints/
    - backend/tests/
    - backend/scripts/
    - angular-app/
    - angular-app/src/app/core/
    - proxy/
    - cron/
    - .github/workflows/
  components:
    - angular-app
    - backend
    - auth
    - data services
    - integration clients
    - api endpoints
    - task manager
    - backend/scripts
    - cron
    - proxy
shallow:
  paths:
    - backend/app/services/data_manager_v2.py
    - backend/app/services/data_sync_service.py
    - backend/app/services/assistant_service.py
    - backend/app/services/analytics_service.py
    - backend/app/services/photo_service.py
    - angular-app/src/app/features/
    - docs/
```
