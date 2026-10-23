# Reverse Engineering Timestamp

## Run Record

- Date: 2026-10-20
- Commit: f791f06d14f41ec44884ab55314c6daaf4b9dae1

## Alcance del escaneo

**Refresco incremental enfocado en la vista de Mercado del frontend y sus
endpoints para F3** (focused scan, NO reconstrucción desde cero) para la etapa
reverse-engineering del intent `261020-mercado-pujas` (F3: pantalla nativa de
Mercado + puja/cancelación como 2ª pestaña del TabView tras Presupuesto). Proyecto
brownfield `futmondo-analytics` (repo raíz, sin repos registrados). Profundidad:
Standard.

El store previo (`261019-presupuesto-selector-cam`, F2) era `partial` con
fingerprint `516d43be98c8f0ce8e7f8b5889cb34d5f3b6d317` sobre la capa nativa iOS
(`ios/`: `FutmondoKit` + `FutmondoApp`) y las áreas Budget/championship. El commit
del repo **no ha cambiado** desde F2 (mismo `f791f06d…`): el código es idéntico.
Lo único que F2 dejó shallow/fuera y F3 necesita en profundidad es la **vista de
Mercado del frontend Angular y sus endpoints de backend**, fuente de verdad del
comportamiento de F3.

Regla de merge aplicada (store previo CURRENT/partial frente a este run enfocado):
se **preserva** la prosa de los 9 artefactos previos (incluida la capa iOS
`FutmondoKit`/`FutmondoApp` y Budget) y se **extiende** con los componentes de
Mercado (`component-inventory`) y sus endpoints (`api-documentation`).
`analyzed.paths`/`analyzed.components` recogen **solo** los paths de ESTE run
(Mercado); la cobertura profunda previa de F2 (capa iOS + Budget + endpoints de
F2) se **degrada a `shallow.paths`**. `kind: partial` (sin `./`).

### Analizado en profundidad (leído y entendido)

- `angular-app/src/app/features/market/market.component.ts` — `MarketComponent`
  (standalone, `OnPush`): interface `MarketPlayer` (~28 campos), signals
  `loading`/`error`/`bidding`/`userInfo`/`viewMode`/`sortField`, `loadData` (GET
  `/api/v1/market/today`), `confirmBid` (POST `/api/v1/market/bid`, query
  `championship_id`/`player_id`/`player_slug`/`price`/`is_clause=false`),
  `cancelBid` (POST `/api/v1/market/cancelbid`, query `championship_id`/`bid_id`),
  `openSofascoreDetail`, `sortCards` descendente, `sortOptions`
  value/change/sofascore_rating/starter_pct/suggested_bid/points/average,
  `viewMode` cards\|table en `localStorage`.
- `angular-app/src/app/features/market/market.component.html` — banner
  `user_info` (balance / en pujas / balance−pujas / puja máxima / disponible);
  vistas `table` y `cards` (avatar, nombre, equipo+team_logo, badges Sofascore y
  %titular, chips posición, grid VALOR/TENDENCIA/PRECIO MERCADO/SUGERIDA/PUNTOS/
  MEDIA, acción PUJAR o fila 'Puja activa'+cancelar, `favorite-card`/`favorite-row`).
- `angular-app/src/app/features/market/bid-dialog.component.ts` — `BidDialogData`
  (`playerName`/`team`/`suggestedBid`/`marketPrice`/`maxBid`), default
  `suggestedBid`, validación mín=`marketPrice` / máx=`maxBid` / vacío-o-`<=0`,
  `BidDialogResult { confirmed, price }`.
- `angular-app/src/app/features/market/confirm-dialog.component.ts` —
  confirmación genérica usada para cancelar puja (devuelve `boolean`).
- `angular-app/src/app/features/market/sofascore-detail-dialog.component.{ts,html}`
  — `SofascoreStats`, carga async `GET /api/v1/sofascore/player/{name}`, rating
  hero + grid de ~16 stats, estados loading/error/404.
- `backend/app/api/v1/endpoints/market.py` — router de Mercado: `/today`, `/bid`,
  `/cancelbid`; contrato real de `players`, `user_info` y el proxy a la API
  Futmondo; validación de boundary del precio (`422`).
- `backend/app/api/v1/endpoints/sofascore_detail.py` — `GET /player/{name}`
  (router `/api/v1/sofascore`, no `/market/*`): shape de `SofascoreStats` y
  `starter_pct = round(matches_started/38*100)`.

### Solo ojeado (sin lectura profunda)

- `market.component.scss`, `sofascore-detail-dialog.component.scss`,
  `bid-dialog.component.spec.ts` — por nombre (estilos / spec no abiertos línea a
  línea).
- Componentes compartidos usados por Mercado
  (`sofascore-badge`, `starter-badge`, `position-chip`, `view-toggle`,
  `loading-state`, `page-header`, `money.pipe`, `player.utils`) — referenciados
  por import, no re-analizados aquí.
- Cobertura profunda del store previo de F2 (`261019-presupuesto-selector-cam`):
  capa nativa iOS `ios/`, Budget/championship y los endpoints de F2
  (`balances.py`, `user.py`, `championships.py`). Preservada en prosa y degradada
  a shallow en este run.

### Dejado fuera (no abierto)

- Resto de `backend/` fuera de `market.py` y `sofascore_detail.py`.
- Resto de `angular-app/` fuera de `features/market/`.
- `ios/.build/`, `ios/xtool/`, `ios/.bsp/`, `ios/.sourcekit-lsp/` (salidas de
  build / caches, no fuente).
- `.github/workflows/`, `docs/`, `cron/`, `proxy/`, `spikes/`, `scripts/`.
- Instalación de AI-DLC (`.kiro/`, `.claude/`, `.codex/`, `.cursor/`, `.aidlc/`,
  `aidlc/`) y secciones AI-DLC de `AGENTS.md`/`.gitignore`.
- Build outputs / deps / caches (`node_modules/`, `.angular/`, `dist/`,
  `coverage/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`).

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 261020-mercado-pujas
fingerprint: 91bea54f4c5fef127edfff7c22d82934d8951bb1
analyzed:
  paths:
    - angular-app/src/app/features/market/
    - backend/app/api/v1/endpoints/market.py
    - backend/app/api/v1/endpoints/sofascore_detail.py
  components:
    - MarketComponent
    - BidDialogComponent
    - ConfirmDialogComponent
    - SofascoreDetailDialogComponent
    - Market router
    - Sofascore detail router
shallow:
  paths:
    - ios/
    - angular-app/src/app/features/budget/
    - angular-app/src/app/core/services/budget.service.ts
    - angular-app/src/app/core/services/championship.service.ts
    - angular-app/src/app/core/models/budget.model.ts
    - backend/app/api/v1/endpoints/balances.py
    - backend/app/api/v1/endpoints/championships.py
    - backend/app/api/v1/endpoints/user.py
    - angular-app/src/styles.scss
    - angular-app/src/app/app.scss
    - angular-app/src/app/features/login/
    - angular-app/src/app/core/
    - angular-app/src/app/shared/
    - angular-app/angular.json
    - backend/app/main.py
    - backend/app/auth/
    - backend/app/core/config.py
    - backend/app/services/
    - backend/app/api/v1/endpoints/
    - backend/requirements.txt
    - backend/pytest.ini
    - backend/ruff.toml
    - angular-app/package.json
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - README.md
    - backend/tests/
```

## Sources

- Herramientas de lectura/listado sobre el repo `/home/javi/futmondo-analytics`.
- `aidlc engine workspace codekb-scope-diff --repo futmondo-analytics --mint
  --paths angular-app/src/app/features/market/,backend/app/api/v1/endpoints/market.py,backend/app/api/v1/endpoints/sofascore_detail.py`
  (fingerprint `91bea54f4c5fef127edfff7c22d82934d8951bb1`) y
  `git rev-parse HEAD` (commit `f791f06d14f41ec44884ab55314c6daaf4b9dae1`).

## Assumptions & Open Questions

- Store previo `261019-presupuesto-selector-cam` (F2, `partial`, fingerprint
  `516d43be…`): por ser un refresco enfocado sobre la vista de Mercado,
  `analyzed.paths`/`analyzed.components` recogen solo los de ESTE run y toda la
  cobertura profunda previa (capa iOS + Budget + endpoints de F2) se degradó a
  `shallow.paths`; la prosa de los 9 artefactos se preservó y se extendió con los
  componentes y endpoints de Mercado.
- El commit del repo es el MISMO que en F2 (`f791f06d…`); el código fuente no ha
  cambiado desde entonces. El refresco es puramente de **cobertura** (profundizar
  en Mercado), no de contenido nuevo del repo.
- `kind: partial`, por lo que `analyzed.paths` NO incluye `./` (no fue un escaneo
  completo del repo).
- El `fingerprint` se minteó sobre los `analyzed.paths` de este run con
  `codekb-scope-diff --mint` y se pegó verbatim.
- El diálogo de detalle Sofascore consume `GET /api/v1/sofascore/player/{name}`
  (router `sofascore_detail.py`), NO un endpoint `/market/*`: así se documenta en
  `api-documentation.md` para evitar que F3 asuma un contrato de Mercado erróneo.
