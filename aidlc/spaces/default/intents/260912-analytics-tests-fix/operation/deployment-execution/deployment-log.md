# Log de Ejecución de Despliegue

## Contexto
Despliegue del arreglo de tests de `AnalyticsService` por el pipeline existente
`.github/workflows/fly-deploy.yml`, disparado por push a `main`. El commit del
arreglo (Commit A del plan de integración) más los commits de integración
B–F y los arreglos de frontend-CI se apilaron sobre `main`.

## Secuencia ejecutada (GitHub Actions)
1. **verify** (BLOQUEANTE): pytest backend + `ng test` frontend.
   - Backend: **54 passed** (Python 3.12). Solo warning inofensivo de Starlette/httpx.
   - Frontend: tras sincronizar `package-lock.json` y corregir la config del builder
     `@angular/build:unit-test` (quitar `karmaConfig`, usar `ChromeHeadless`),
     `ng test` pasa.
2. **deploy backend**: `fly deploy` de `futmondo-api` — OK.
3. **deploy frontend**: `fly deploy` de `futmondo-app` — OK.
4. **smoke test** `/health`: **OK**.

## Resultado
- **Despliegue exitoso.** Gate de CI desbloqueado; el bugfix está en producción.

## Incidencias resueltas durante el despliegue
- `npm ci` falló por `package-lock.json` desincronizado → regenerado con
  `npm install --package-lock-only` y committeado.
- `ng test` falló por `karmaConfig` no soportado por el builder unit-test →
  eliminado de `angular.json`; browser alineado a `ChromeHeadless` en los workflows.

## Migraciones de BD
- Ninguna (el cambio es solo un fichero de test).
