# Developer Scan — futmondo-analytics (lead-only pipeline)

> Chain lead-only (collaborators off): el developer agent escaneó y sintetizó los 9
> artefactos de la CodeKB directamente. Este fichero es el handoff que el receipt del link
> requiere; el cuerpo del análisis vive en la CodeKB publicada
> (`aidlc/spaces/default/codekb/futmondo-analytics/`).

## Developer Code Scan Results

Scan focalizado del frontend Angular para el estudio de viabilidad de reescritura nativa iOS
(Swift/SwiftUI con xtool). Analizadas en profundidad las 5 pantallas núcleo
(`features/{login,market,budget,favorites,calculator}`) y la capa `core/` (servicios,
interceptor, guard, modelos), con foco en: qué hace cada pantalla, el flujo de auth (access en
memoria + refresh en cookie HttpOnly, relevante a la migración a Keychain) y la superficie de
API que el cliente nativo debe consumir. Merge sobre store STALE: `kind: partial`, cobertura
profunda previa degradada a shallow.

### Scan Coverage

- **Analizado en profundidad (este run)**: `angular-app/src/app/features/login/`, `.../market/`,
  `.../budget/`, `.../favorites/`, `.../calculator/`, `angular-app/src/app/core/` (auth.service,
  auth.interceptor, auth.guard, budget.service, favorites.service, roster.service, sync.service,
  championship.service, models).
- **Skimmed (shallow)**: `features/splash/`, `shared/`, `app.routes.ts`, y la cobertura profunda
  previa del store (angular-app completo, backend, proxy, cron, docs, workflows) degradada a
  shallow por no reverificarse en este run.
- **No abierto**: build outputs, node_modules, dist, .angular, instalación de AI-DLC.

## Handoff Summary

9 artefactos sintetizados y publicados en `aidlc/spaces/default/codekb/futmondo-analytics/`.
Concerns: (1) las 5 pantallas tienen cobertura de test fina (sólo ~2 de ~10 componentes con
spec); la especificación de referencia descansa sobre lectura de código, con
`calculator.component.spec.ts` codificando invariantes de saldo futuro. (2) Tipado débil
(`any`) en FavoritesService/RosterService y en respuestas de market/favorites — riesgo para
generar modelos `Codable` fiables en Swift. (3) El flujo de refresh basado en cookie HttpOnly
confirma la dependencia D-01 para el cliente nativo (Keychain + posible ajuste de
`/auth/refresh`).
