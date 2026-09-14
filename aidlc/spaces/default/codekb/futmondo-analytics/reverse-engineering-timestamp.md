# Reverse Engineering — Registro de Ejecución

> Registro de cuándo se realizó el reverse-engineering y del alcance analizado.
> El bloque `## Scope of Analysis` es leído por `codekb-scope-diff` en el próximo
> rerun, por lo que refleja lo que este escaneo cubrió realmente.

## Metadatos de ejecución

- **Fecha**: 2026-09-13T05:44:07Z
- **Commit hash**: `099e223` (fingerprint del scope acuñado sobre las
  `analyzed.paths` de este run; el commit del árbol de trabajo se resuelve en
  build)
- **Tipo de escaneo**: FOCUSED sobre store previo STALE (re-síntesis parcial)
- **Profundidad**: Minimal
- **Tipo de proyecto**: Brownfield
- **Scope**: bugfix
- **Repo**: repo único (workspace root), `/home/javi/futmondo-analytics`
- **Intent**: 260912-analytics-tests-fix
- **Pipeline**: developer (escaneo) → architect (síntesis, este artefacto)

## Alcance y notas

Rerun ENFOCADO sobre `backend/app/services/` (con `analytics_service.py`
re-verificado en profundidad) y `backend/tests/` (suite de caracterización,
`test_analytics_service.py`). El store previo era un escaneo FULL
(`intent: analisis-mejoras`, `kind: full`) hoy STALE: su prosa se PRESERVA, pero
sus `analyzed.paths` profundas se DEGRADAN a `shallow.paths` porque esa cobertura
profunda no se pudo re-verificar en este run. Solo el componente `data services`
se re-verificó en profundidad; el resto del inventario se conserva del escaneo
previo. La huella (`fingerprint`) se acuñó con `codekb-scope-diff --mint` sobre
`backend/app/services/,backend/tests/`.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 260912-analytics-tests-fix
fingerprint: 099e22398dc485929ac6dffec6fd830befd2bea4
analyzed:
  paths:
    - backend/app/services/
    - backend/tests/
  components:
    - data services
shallow:
  paths:
    - ./
    - backend/
    - backend/app/
    - backend/app/core/
    - backend/app/auth/
    - backend/app/api/v1/endpoints/
    - backend/scripts/
    - angular-app/
    - angular-app/src/app/core/
    - angular-app/src/app/features/
    - proxy/
    - cron/
    - .github/workflows/
    - docs/
    - backend/app/services/data_manager_v2.py
    - backend/app/services/data_sync_service.py
    - backend/app/services/assistant_service.py
    - backend/app/services/photo_service.py
```
