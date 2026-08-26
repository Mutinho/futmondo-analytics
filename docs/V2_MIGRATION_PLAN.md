# Plan de Migración v2.0 — Futmondo Analytics

**Fecha:** 26 agosto 2026  
**Objetivo:** Refactorizar backend (seguridad, limpieza) y frontend (componentización, DRY) para versión 2.0  
**Estimación total:** 12-16 horas

---

## Fase 1: Security Fixes Backend (30 min)

### 1.1 Fix CORS — Whitelist origins
**Archivo:** `backend/app/main.py:65-66`  
**Problema:** `allow_origins=["*"]` con `allow_credentials=True` permite que cualquier web haga requests autenticados.  
**Solución:**
```python
ALLOWED_ORIGINS = [
    "https://futmondo-app.fly.dev",
    "http://futmondo.localhost",
    "http://localhost:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    ...
)
```

### 1.2 JWT_SECRET — Fail en producción si no está seteado
**Archivo:** `backend/app/core/config.py:73`  
**Problema:** Fallback hardcoded `"futmondo-dev-secret-change-in-prod"` — tokens forjables si se olvida el env var.  
**Solución:**
```python
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    if os.getenv("FLY_APP_NAME"):
        raise RuntimeError("JWT_SECRET must be set in production")
    JWT_SECRET = "futmondo-dev-secret-change-in-prod"
```

### 1.3 Eliminar disable global de SSL
**Archivo:** `backend/app/main.py:7-8`  
**Problema:** Desactiva verificación SSL para TODO el proceso Python.  
**Solución:** Eliminar las líneas. Si Docker necesita CA certs, instalarlos en el Dockerfile.

### 1.4 Fix `adapt_params` en analytics.py
**Archivo:** `backend/app/api/v1/endpoints/analytics.py`  
**Problema:** SQL usa `%s` hardcoded sin `db.adapt_params()`.  
**Solución:** Envolver todas las queries con `db.adapt_params(sql)`.

### 1.5 Eliminar passwords en memoria (opcional — requiere cambio de flujo)
**Archivo:** `backend/app/auth/session_store.py`  
**Problema:** Password en texto plano en UserSession durante 12h.  
**Solución:** Guardar solo el token de sesión de Futmondo. Re-auth requiere nuevo login del usuario.

---

## Fase 2: Dead Code Cleanup Backend (15 min)

### 2.1 Eliminar archivos muertos (~130KB)
- `backend/app/services/data_manager_patched.py` (47KB)
- `backend/app/services/data_manager.py` (2KB)
- `backend/app/services/analyzers.py` (17KB)
- `backend/app/services/team_analyzer.py` (15KB)
- `backend/app/services/data_initializer.py`

### 2.2 Eliminar `FutmondoService` y sus dependencias
- `backend/app/services/futmondo_service.py`
- Quitar `Depends(FutmondoService)` de `sofascore_sync.py` y `user_stats.py`

### 2.3 Limpiar requirements.txt
- Eliminar `sqlalchemy>=2.0.23` (nunca usado)
- Evaluar si `libsql-experimental` sigue siendo necesario

### 2.4 Extraer `LALIGA_TEAMS` a constante compartida
**Crear:** `backend/app/core/constants.py`  
**Eliminar de:** sync.py, analytics.py, clausulable_players.py, favorites.py, transactions.py, analytics_service.py (6 duplicados)

### 2.5 Extraer helpers duplicados
**Crear:** En `backend/app/api/v1/endpoints/_helpers.py` añadir:
- `clean_float(val, default=None)` — limpieza de NaN/None
- Unificar `get_championship_config()` con todos los campos (presupuesto, premios, ranking_mode, etc.)

---

## Fase 3: Shared Styles + Utils Frontend (1-2h)

### 3.1 Crear shared SCSS parciales
```
angular-app/src/app/shared/styles/
├── _player-card.scss      # Card styles (header, avatar, badges, stats-grid)
├── _table-common.scss     # Table container, player-photo, team-logo, position chips
├── _loading-states.scss   # Loading spinner, error message, empty state
├── _responsive-grid.scss  # Cards container responsive breakpoints
└── _index.scss            # Re-exports all
```

### 3.2 Crear `player.utils.ts`
**Archivo:** `angular-app/src/app/shared/utils/player.utils.ts`
```typescript
export function getPlayerPhoto(slug: string): string { ... }
export function getTeamLogo(logo: string): string { ... }
export function getPositionKey(pos: string): string { ... }
export function getPositionLabel(pos: string): string { ... }
export function onImgError(event: Event): void { ... }
```

### 3.3 Migrar los 6 componentes principales a usar shared styles/utils
- `features/market/market.component.ts`
- `features/favorites/favorites.component.ts`
- `features/my-roster/my-roster.component.ts`
- `features/calculator/calculator.component.ts`
- `features/clausulable/clausulable.component.ts`
- `features/analytics/market/market.component.ts`

---

## Fase 4: Shared Components Frontend (3-4h)

### 4.1 `LoadingStateComponent`
**Archivo:** `shared/components/loading-state.component.ts`  
**Inputs:** `loading: boolean`, `error: string | null`, `emptyMessage: string`, `isEmpty: boolean`  
**Content projection:** `<ng-content>` para el contenido real cuando hay datos.  
**Reemplaza:** El patrón `@if(loading)...@else if(error)...@else` en 15+ componentes.

### 4.2 `ViewToggleComponent`
**Archivo:** `shared/components/view-toggle.component.ts`  
**Inputs:** `viewMode: 'cards' | 'table'`, `sortOptions: {value, label}[]`, `sortField: string`  
**Outputs:** `viewModeChange`, `sortChange`  
**Reemplaza:** El bloque view-toggle + sort dropdown en 7 componentes.

### 4.3 `PlayerCardComponent`
**Archivo:** `shared/components/player-card.component.ts`  
**Inputs:** `player: PlayerCardData` (name, slug, team, team_logo, position, sofascore_rating, starter_pct, stats: {label, value}[])  
**Content projection:** `<ng-content select="[card-actions]">` para botones custom.  
**Reemplaza:** La card de jugador idéntica en 6 componentes (~200 líneas cada una).

### 4.4 `PositionChipComponent`
**Archivo:** `shared/components/position-chip.component.ts`  
**Inputs:** `position: string`  
**Reemplaza:** El `<span class="pos-chip"...>` en 8 componentes.

### 4.5 `InfoBannerComponent`
**Archivo:** `shared/components/info-banner.component.ts`  
**Inputs:** `items: {label: string, value: string, class?: string}[]`  
**Reemplaza:** El banner de resumen en market, my-roster, calculator.

---

## Fase 5: Extract Inline Templates (2-3h)

### Criterio: Mover a .html/.scss si el template tiene >90 líneas

| # | Componente | Template (líneas) | Estilos (líneas) |
|---|-----------|-------------------|------------------|
| 1 | `features/market/market.component.ts` | ~278 | ~120 |
| 2 | `features/analytics/market/market.component.ts` | ~298 | ~100 |
| 3 | `features/calculator/calculator.component.ts` | ~263 | ~140 |
| 4 | `features/my-roster/my-roster.component.ts` | ~286 | ~130 |
| 5 | `features/favorites/favorites.component.ts` | ~232 | ~120 |
| 6 | `features/transactions/transactions.component.ts` | ~229 | ~100 |
| 7 | `features/clausulable/clausulable.component.ts` | ~189 | ~80 |
| 8 | `features/classification/classification.component.ts` | ~128 | ~50 |
| 9 | `shared/components/assistant-chat.component.ts` | ~109 | ~100 |
| 10 | `features/budget/sync-dialog/sync-dialog.component.ts` | ~90 | ~60 |
| 11 | `features/settings/championships-config.component.ts` | ~90 | ~60 |
| 12 | `features/market/sofascore-detail-dialog.component.ts` | ~135 | ~50 |

**Formato resultado:**
```
component.ts      → solo lógica (class + imports)
component.html    → template
component.scss    → estilos
```

**NO mover** (muy pequeños, OK inline):
- page-header, scroll-top, info-card, sofascore-badge, starter-badge, assistant-fab, confirm-dialog, splash, analytics-shell, position-chip

---

## Fase 6: Split Large Components (2-3h)

### 6.1 Consolidar market y analytics/market
**Problema:** `features/market/` y `features/analytics/market/` comparten ~80% del código.  
**Solución:** Crear un `PlayerListComponent` genérico configurable via inputs (showBidButton, showWatchlistButton, dataSource, columns) y reusar en ambas páginas.

### 6.2 Extract de calculator
- `CalculatorHeaderComponent` — cabecera con saldo/en-venta/seleccionadas
- `OnSaleSectionComponent` — tarjetas naranjas de jugadores en venta

### 6.3 Extract de transactions
- `TransactionFiltersComponent` — búsqueda + filtros
- `TransactionGroupComponent` — bloque por fecha con sus filas

### 6.4 Extract de my-roster
- `SellRecommendationsWidget` — sección de "recomendados para vender"

---

## Fase 7: Minor Improvements (1h)

### 7.1 Backend
- Usar `ThreadedConnectionPool` en vez de `SimpleConnectionPool`
- Normalizar `db_type` ("postgres" → "postgresql")
- Añadir rate limiting en `/auth/login` (5 intentos/min/IP)
- Mover endpoint de photos de `main.py` a router propio
- Convertir `except Exception: pass` a `logger.debug()`

### 7.2 Frontend
- Añadir `ChangeDetectionStrategy.OnPush` a todos los componentes (signals lo permite)
- Convertir `@Input()` decorators a `input()` signal inputs en shared components
- Considerar `@defer` para componentes pesados (charts, analytics)

---

## Orden de ejecución recomendado

```
Fase 1 (30 min) → Fase 2 (15 min) → Fase 3 (1-2h) → Fase 4 (3-4h) → Fase 5 (2-3h) → Fase 6 (2-3h) → Fase 7 (1h)
```

**Total estimado: 12-16 horas**

---

## Criterios de éxito v2.0

- [ ] 0 vulnerabilidades de seguridad críticas
- [ ] 0 archivos de código muerto
- [ ] Shared components eliminan >1000 líneas duplicadas
- [ ] Todos los componentes >90 líneas de template usan .html externo
- [ ] LALIGA_TEAMS definido en un solo lugar
- [ ] Utils (getPlayerPhoto, etc.) definidos en un solo lugar
- [ ] CSS compartido via SCSS parciales (no copy-paste)
- [ ] Build exitoso + app funcional en Docker
- [ ] Deploy a producción
