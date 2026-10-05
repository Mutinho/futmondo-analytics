# Frontend Components — No aplica

## Aplicabilidad

Este artefacto es CONDITIONAL: sólo tiene contenido si la unidad incluye
frontend/UI. El intent `261005-data-manager-god-file` es un **refactor
backend-puro**: descompone `backend/app/services/data_manager_v2.py` (capa de
acceso a datos Python) al patrón DDD, preservando la superficie pública exacta.

No hay componentes de frontend que diseñar:

- No se crean ni modifican componentes Angular.
- No cambian props, estado, flujos de interacción ni validación de formularios.
- No cambian los endpoints ni los payloads que la PWA consume (equivalencia
  funcional estricta, FR3.1): el frontend no percibe el refactor.

El `angular-app/` queda explícitamente **fuera de alcance** (ver `requirements.md`
→ Fuera de alcance).

## Consecuencia para el diseño

El diseño funcional de este intent vive en `entities.md` (módulos-objetivo del
refactor), `rules.md` (invariantes) y `functional-spec.md` (workflow de
extracción y máquina de estados). No hay dependencia de UI ni punto de
integración de frontend que especificar.
