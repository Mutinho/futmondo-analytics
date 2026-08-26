# Plan de Mejoras Frontend — Post v2.0

**Fecha:** 26 agosto 2026  
**Origen:** Deep audit segunda pasada  
**Total issues:** 24 (5 High, 11 Medium, 8 Low)  
**Estimación total:** 4-6 horas

---

## Fase A: HIGH Priority (30-40 min)

### A.1 OnPush en TODOS los feature components
**Archivos:** 9 componentes
- `features/market/market.component.ts`
- `features/favorites/favorites.component.ts`
- `features/my-roster/my-roster.component.ts`
- `features/calculator/calculator.component.ts`
- `features/clausulable/clausulable.component.ts`
- `features/transactions/transactions.component.ts`
- `features/evolution/evolution.component.ts`
- `features/budget/budget-overview/budget-overview.component.ts`
- `features/classification/classification.component.ts`

**Acción:** Añadir `changeDetection: ChangeDetectionStrategy.OnPush` + importar `ChangeDetectionStrategy`.

### A.2 Migrar 3 componentes restantes a shared utils
**Archivos:**
- `features/clausulable/clausulable.component.ts`
- `features/transactions/transactions.component.ts`
- `features/calculator/calculator.component.ts`

**Acción:**
- Importar `getPlayerPhoto, getTeamLogo, getPositionKey, getPositionLabel, onImgError` de `shared/utils/player.utils`
- Asignar como class properties: `getPlayerPhoto = getPlayerPhoto;`
- Eliminar los métodos duplicados del class body

### A.3 Extraer SpanishDateAdapter a shared
**Crear:** `shared/utils/spanish-date-adapter.ts`

**Contenido:** La clase `SpanishDateAdapter extends NativeDateAdapter` + `ES_DATE_FORMATS` const.

**Archivos a modificar:**
- `features/calculator/calculator.component.ts` — eliminar clase interna, importar de shared
- `features/transactions/transactions.component.ts` — eliminar clase interna, importar de shared

### A.4 Fix Auth Guard race condition
**Archivo:** `core/guards/auth.guard.ts`

**Acción:** Hacer el guard async — esperar a que `AuthService.initialized()` sea true antes de verificar el token:
```typescript
export const authGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  // Wait for session recovery to complete
  let attempts = 0;
  while (!auth.initialized() && attempts < 40) { // max 2s
    await new Promise(r => setTimeout(r, 50));
    attempts++;
  }
  if (auth.getAccessToken()) return true;
  inject(Router).navigate(['/login']);
  return false;
};
```

**Prerequisito:** Verificar que `AuthService` tiene un signal `initialized` (o añadirlo si no existe).

### A.5 Fix proxy.conf.json
**Archivo:** `proxy.conf.json`

**Acción:** Añadir regla para `/auth`:
```json
"/auth": {
  "target": "http://localhost:8000",
  "secure": false,
  "changeOrigin": true
}
```

---

## Fase B: MEDIUM Priority — Servicios y Arquitectura (1-2h)

### B.1 Tipar AnalyticsService (eliminar `any`)
**Archivo:** `core/services/analytics.service.ts`

**Acción:** Crear interfaces para los 13 endpoints:
- `ClassificationResponse`, `HeatmapResponse`, `TrendsResponse`, etc.
- Cambiar `Promise<any>` a `Promise<ClassificationResponse>`, etc.

### B.2 Extraer `isMobile` a utility inyectable
**Crear:** `shared/utils/responsive.ts`
```typescript
export function injectIsMobile() {
  const bp = inject(BreakpointObserver);
  return toSignal(bp.observe([Breakpoints.Handset]).pipe(map(r => r.matches)), { initialValue: false });
}
```

**Modificar:** 9 componentes que repiten el patrón — reemplazar con `isMobile = injectIsMobile();`

### B.3 Preloading strategy + async animations
**Archivo:** `app.config.ts`

**Acción:**
```typescript
import { PreloadAllModules, withPreloading } from '@angular/router';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

provideRouter(routes, withPreloading(PreloadAllModules)),
provideAnimationsAsync(),  // en vez de provideAnimations()
```

### B.4 Fix Auth Interceptor — encolar requests en refresh
**Archivo:** `core/interceptors/auth.interceptor.ts`

**Acción:** Implementar patrón estándar con BehaviorSubject:
- Cuando llega un 401 y `isRefreshing = true`, encolar el request en un Subject
- Cuando el refresh completa, emitir el nuevo token y replay todos los encolados
- Si el refresh falla, rechazar todos

### B.5 Caching en servicios (evolution, stats)
**Archivos:** `evolution.service.ts`, `stats.service.ts`

**Acción:** Añadir signal-based cache con TTL (5 min):
```typescript
private cache = signal<T | null>(null);
private cacheExpiry = 0;
async getData(...) {
  if (this.cache() && Date.now() < this.cacheExpiry) return this.cache()!;
  const res = await fetch...;
  this.cache.set(res);
  this.cacheExpiry = Date.now() + 5 * 60_000;
  return res;
}
```

### B.6 NGSW — cachear fonts e imágenes externas
**Archivo:** `ngsw-config.json`

**Añadir dataGroups:**
```json
{
  "name": "google-fonts",
  "urls": ["https://fonts.googleapis.com/**", "https://fonts.gstatic.com/**"],
  "cacheConfig": { "strategy": "performance", "maxSize": 10, "maxAge": "365d" }
},
{
  "name": "futmondo-static",
  "urls": ["https://static01.mondocore.com/**", "https://static02.mondocore.com/**"],
  "cacheConfig": { "strategy": "performance", "maxSize": 500, "maxAge": "7d" }
}
```

### B.7 Fix Inter font (eliminar o cargar)
**Archivo:** `styles.scss`

**Acción:** Eliminar `'Inter'` del font stack. Solo usar `'Roboto', sans-serif` que es lo que realmente se carga.

### B.8 Extraer teamLogoMap a shared constant
**Crear:** `shared/utils/team-logos.ts`

**Contenido:** Mapa de team_id → logo filename (mismo que está en clausulable y analytics/market).

**Modificar:** clausulable.component.ts, analytics/market/market.component.ts — importar de shared.

### B.9 Error feedback en clausulable y classification
**Archivos:** `clausulable.component.ts`, `classification.component.ts`

**Acción:** En el `catch`:
```typescript
catch (e) {
  this.error.set('Error al cargar datos. Inténtalo de nuevo.');
}
```
Y verificar que el template muestra el error (via LoadingStateComponent o directamente).

### B.10 Calculator — Crear RosterService
**Crear:** `core/services/roster.service.ts`

**Métodos:**
- `getMyRoster(championshipId)`
- `getOnSale(championshipId)`
- `sell(championshipId, playerIds, projectedDate?)`
- `cancelSale(championshipId, playerId)`

**Modificar:** calculator.component.ts — reemplazar HttpClient directo con RosterService.

### B.11 Favorites — Crear FavoritesService
**Crear:** `core/services/favorites.service.ts`

**Métodos:**
- `getMyFavorites(championshipId)`
- `unfollow(championshipId, playerId)`

**Modificar:** favorites.component.ts — reemplazar HttpClient directo.

---

## Fase C: LOW Priority (1h)

### C.1 Ruta 404 wildcard
**Archivo:** `app.routes.ts`

**Añadir al final:**
```typescript
{ path: '**', redirectTo: '/budget' }
```

### C.2 Material Icons — display=swap
**Archivo:** `index.html`

**Cambiar** el `<link>` de Material Icons a incluir `&display=swap`.

### C.3 Body inline style → CSS class
**Archivo:** `index.html` + splash component

**Cambiar** `<body style="...">` a `<body class="splash-bg">` y mover el estilo a una clase CSS global.

### C.4 @defer para AssistantFab
**Archivo:** `app.html`

**Cambiar:**
```html
<app-assistant-fab />
```
a:
```html
@defer (on idle) {
  <app-assistant-fab />
}
```

### C.5 Build optimization — inlineCritical
**Archivo:** `angular.json`

**Añadir a la config de producción:**
```json
"optimization": {
  "scripts": true,
  "styles": { "minify": true, "inlineCritical": true }
}
```

### C.6 Router subscription cleanup
**Archivo:** `app.ts`

**Añadir** `takeUntilDestroyed()` a la suscripción de router.events.

### C.7 Abort signal para askStream (dead code pero buena práctica)
**Archivo:** `core/services/assistant.service.ts`

**Acción:** Añadir `signal?: AbortSignal` param a `askStream()`, pasarlo a `fetch()`.

### C.8 Bundle budget — reducir warning
**Archivo:** `angular.json`

**Cambiar** budget warning de 500kB a 400kB para detectar regresiones antes.

---

## Orden de ejecución

```
Fase A (30-40 min) → Fase B (1-2h) → Fase C (1h)
```

**Total estimado: 3-4 horas**

---

## Criterios de éxito

- [ ] 0 componentes sin OnPush (shared + features)
- [ ] 0 duplicados de player.utils (getPlayerPhoto, etc.)
- [ ] SpanishDateAdapter en un solo lugar
- [ ] Auth guard maneja deep links correctamente
- [ ] proxy.conf.json incluye /auth
- [ ] AnalyticsService tipado (no `any`)
- [ ] isMobile definido en un solo lugar
- [ ] NGSW cachea fonts + imágenes externas
- [ ] Build exitoso + app funcional
