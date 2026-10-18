# Unit Test Instructions — Spike de la cadena `xtool` (B-01)

## Naturaleza del testing en este spike

Este spike **no introduce código de aplicación testeable** en el repo (no toca `backend/` ni
`angular-app/`). Conforme al Testing Contract (`test-after`, `minimal`, scope `bugfix`):

- **No hay suite automatizada nueva** para la cadena `xtool`: su verificación (build → firma →
  instalación → arranque en el iPhone) es **manual en dispositivo** y no automatizable como CI a
  coste 0 €.
- La **obligación de testing** es que la **suite existente del repo siga verde**. Como el spike
  solo añade ficheros nuevos bajo `spikes/ios-xtool/` y `docs/spikes/`, no debería afectarla.

## Verificación de que la suite existente sigue verde (comandos acotados)

Ejecutados por la etapa Build and Test. No es un `npm test` global; se corre la suite existente
tal cual:

- Backend (desde `backend/`):
  ```bash
  pytest
  ```
- Frontend (desde `angular-app/`):
  ```bash
  npm run test
  ```

Expectativa: **sin regresiones** respecto al baseline (el spike no modifica código de app).

## Smoke test manual del spike (el "test" real del DONE)

Este es el criterio de aceptación del spike, verificado a mano con el iPhone 13 Pro conectado:

1. Correr `spikes/ios-xtool/scripts/setup-wsl.sh` (idempotente) hasta dejar el toolchain listo.
2. Correr `spikes/ios-xtool/scripts/smoke.sh` (equiv. a `xtool dev build` → firma → instalación).
3. **Evidencia de éxito**: la app aparece en el iPhone 13 Pro y, al abrirla, muestra la pantalla
   trivial ("xtool OK" + versión). Capturar foto/log de `xtool` en la nota de hallazgos de
   `docs/spikes/ios-xtool.md`.
4. **Repetibilidad**: el mismo `smoke.sh` sirve para reinstalar/refirmar tras la caducidad ~7
   días (fuera de foco, pero la receta queda lista).

## Objetivos de cobertura

No aplica un piso de cobertura nuevo (spike de toolchain, sin código de app). El trinquete de
cobertura del repo (backend `--cov-fail-under`, frontend `coverageThresholds`) **no se toca** y
**no se relaja**.

## Mocking / datos de prueba

No aplica: la app del spike no tiene red ni datos (una pantalla estática trivial).
