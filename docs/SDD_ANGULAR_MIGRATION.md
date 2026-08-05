# SDD - Migración Frontend Futmondo a Angular 22

**Fecha:** 2026-08-04  
**Estado:** Propuesta  
**Angular:** v22 (signal-first, Signal Forms, Resource API estables)  
**UI:** Angular Material 22

---

## 1. Contexto y Motivación

### Estado actual
- Frontend monolítico: 1 archivo HTML + 1 app.js de ~3500 líneas (JavaScript vanilla)
- CSS inline sin sistema de diseño
- Sin tipado, sin tests, sin componentización
- UX arcaica y poco atractiva visualmente
- Funcionalidades de IA (humor/crónicas con OpenAI) **eliminadas del scope**
- Sistema de login/premium **eliminado** — todo el contenido es público, no hay roles ni autenticación de usuario

### Objetivo
Migrar a un frontend moderno con **Angular 22** + **Angular Material 22** que ofrezca:
- UI profesional y responsive (Material Design 3)
- Código mantenible, tipado y testeable
- Componentes standalone con signals
- Mejor experiencia de desarrollo y de usuario
- Acceso total sin login — no existe concepto de usuario premium

---

## 2. Decisión de Diseño: Angular Material vs Bootstrap

### Recomendación: **Angular Material**

| Criterio | Angular Material | ng-bootstrap |
|----------|-----------------|--------------|
| Integración con Angular | Nativa (mismo equipo) | Wrapper de terceros |
| Componentes de datos (tablas, sort) | ✅ mat-table con sort, paginate, filter | Básico, necesitas DataTables aparte |
| Theming | Sistema de temas con paletas | Clases CSS, más manual |
| Gráficos | Combina con ng2-charts (Chart.js wrapper) | Igual |
| Consistencia visual | Material Design 3 | Depende de customización |
| Responsive | CDK layout breakpoints | Grid system CSS |
| Complejidad | Media (más opinado) | Baja (más libre) |

**Razón:** La app tiene muchas tablas con datos financieros y necesita ordenación, filtrado y drill-down. `mat-table` con `MatSort` y `MatPaginator` cubren esto nativamente. Además, los cards, tabs y botones de Material encajan perfectamente con el tipo de dashboard que necesitamos.

---

## 3. Arquitectura Propuesta

### 3.1 Estructura de Proyecto

```
futmondo-angular/
├── src/
│   ├── app/
│   │   ├── core/                      # Servicios singleton, interceptors
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts           # HttpClient base (proxy a backend)
│   │   │   │   ├── sync.service.ts          # Sincronización de datos
│   │   │   │   └── budget.service.ts        # Datos de presupuesto
│   │   │   └── models/
│   │   │       ├── team.model.ts
│   │   │       ├── transaction.model.ts
│   │   │       └── player.model.ts
│   │   │
│   │   ├── shared/                    # Componentes reutilizables
│   │   │   ├── components/
│   │   │   │   ├── money-cell/             # Formato dinero con color
│   │   │   │   ├── loading-spinner/
│   │   │   │   ├── error-message/
│   │   │   │   └── empty-state/
│   │   │   └── pipes/
│   │   │       ├── money.pipe.ts           # Formateo de dinero
│   │   │       └── relative-date.pipe.ts
│   │   │
│   │   ├── features/                  # Módulos por funcionalidad (lazy loaded)
│   │   │   ├── budget/                     # 💰 Presupuesto
│   │   │   │   ├── budget.routes.ts
│   │   │   │   ├── budget-overview/        # Tabla resumen
│   │   │   │   └── budget-detail/          # Detalle altas/bajas
│   │   │   │
│   │   │   ├── evolution/                  # 📊 Evolución
│   │   │   │   ├── evolution.routes.ts
│   │   │   │   ├── points-chart/
│   │   │   │   └── positions-chart/
│   │   │   │
│   │   │   ├── stats/                      # 📈 Estadísticas
│   │   │   │   ├── stats.routes.ts
│   │   │   │   ├── players-chart/
│   │   │   │   ├── clauses-chart/
│   │   │   │   └── operations-chart/
│   │   │   │
│   │   │   ├── finances/                   # 💰 Finanzas (premium)
│   │   │   │   └── finances.routes.ts
│   │   │   │
│   │   │   ├── clausulable/                # ⚽ Clausulables (premium)
│   │   │   │   └── clausulable.routes.ts
│   │   │   │
│   │   │   └── analytics/                  # 📊 Analytics Avanzado
│   │   │       ├── analytics.routes.ts
│   │   │       ├── overview/
│   │   │       ├── classification/
│   │   │       ├── players/
│   │   │       ├── users/
│   │   │       ├── market/
│   │   │       ├── opportunities/
│   │   │       └── projections/
│   │   │
│   │   ├── layout/                    # Shell de la app
│   │   │   ├── header/                     # Toolbar con título
│   │   │   └── shell/                      # Layout principal (toolbar + nav + outlet)
│   │   │
│   │   ├── app.component.ts
│   │   ├── app.config.ts
│   │   └── app.routes.ts
│   │
│   ├── environments/
│   ├── styles.scss                    # Tema Material + globals
│   └── index.html
├── angular.json
├── package.json
└── tsconfig.json
```

### 3.2 Routing

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: '', redirectTo: 'budget', pathMatch: 'full' },
  { 
    path: 'budget', 
    loadChildren: () => import('./features/budget/budget.routes') 
  },
  { 
    path: 'evolution', 
    loadChildren: () => import('./features/evolution/evolution.routes') 
  },
  { 
    path: 'stats', 
    loadChildren: () => import('./features/stats/stats.routes') 
  },
  { 
    path: 'finances', 
    loadChildren: () => import('./features/finances/finances.routes') 
  },
  { 
    path: 'clausulable', 
    loadChildren: () => import('./features/clausulable/clausulable.routes') 
  },
  { 
    path: 'analytics', 
    loadChildren: () => import('./features/analytics/analytics.routes') 
  },
];
```

### 3.3 Navegación

Se propone usar **mat-tab-nav-bar** (tabs horizontales como en la versión actual pero con Material Design) para mantener la familiaridad pero con mejor estética:

```html
<!-- shell.component.html -->
<mat-toolbar color="primary">
  <span>🏆 Futmondo</span>
</mat-toolbar>

<nav mat-tab-nav-bar>
  <a mat-tab-link routerLink="/budget" routerLinkActive #rla="routerLinkActive" [active]="rla.isActive">
    💰 Presupuesto
  </a>
  <a mat-tab-link routerLink="/evolution" ...>📊 Evolución</a>
  <a mat-tab-link routerLink="/stats" ...>📈 Estadísticas</a>
  <a mat-tab-link routerLink="/finances" ...>💰 Finanzas</a>
  <a mat-tab-link routerLink="/clausulable" ...>⚽ Clausulables</a>
  <a mat-tab-link routerLink="/analytics" ...>📊 Analytics</a>
</nav>

<main>
  <router-outlet />
</main>
```

### 3.4 Componente de Presupuesto (ejemplo con Angular 22 signals + resource)

```typescript
// budget-overview.component.ts
@Component({
  selector: 'app-budget-overview',
  standalone: true,
  imports: [MatTableModule, MatSortModule, MatButtonModule, MoneyCellComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="budget-header">
      <h2>💰 Presupuesto por Equipo</h2>
      <button mat-raised-button color="accent" (click)="sync()" [disabled]="syncing()">
        {{ syncing() ? '⏳ Sincronizando...' : '🔄 Sincronizar' }}
      </button>
    </div>

    @if (balances.isLoading()) {
      <mat-spinner diameter="40" />
    } @else if (balances.error()) {
      <app-error-message [message]="balances.error()!.message" />
    } @else {
      <mat-table [dataSource]="balances.value()!.teams" matSort>
        <ng-container matColumnDef="team_name">
          <mat-header-cell *matHeaderCellDef mat-sort-header>Equipo</mat-header-cell>
          <mat-cell *matCellDef="let t">{{ t.team_name }}</mat-cell>
        </ng-container>
        <ng-container matColumnDef="balance">
          <mat-header-cell *matHeaderCellDef mat-sort-header>Saldo</mat-header-cell>
          <mat-cell *matCellDef="let t"><app-money-cell [value]="t.balance" /></mat-cell>
        </ng-container>
        <ng-container matColumnDef="performance">
          <mat-header-cell *matHeaderCellDef mat-sort-header>Rendimiento</mat-header-cell>
          <mat-cell *matCellDef="let t"><app-money-cell [value]="t.performance" [signed]="true" /></mat-cell>
        </ng-container>
        <!-- ... más columnas -->
        <mat-header-row *matHeaderRowDef="displayedColumns" />
        <mat-row *matRowDef="let row; columns: displayedColumns" 
                 (click)="openDetail(row)" class="clickable" />
      </mat-table>
    }
  `
})
export class BudgetOverviewComponent {
  private budgetService = inject(BudgetService);
  private router = inject(Router);

  syncing = signal(false);
  displayedColumns = ['team_name', 'balance', 'team_value', 'total_spent', 'total_income', 'performance'];

  // Angular 22 resource API - auto-fetches and tracks loading/error
  balances = resource({
    loader: () => this.budgetService.getBalances(),
  });

  async sync() {
    this.syncing.set(true);
    await this.budgetService.syncTransactions();
    this.balances.reload();
    this.syncing.set(false);
  }

  openDetail(team: TeamBudget) {
    this.router.navigate(['/budget', team.team_id]);
  }
}
```

---

## 4. Tecnologías y Dependencias

| Paquete | Versión | Uso |
|---------|---------|-----|
| @angular/core | ^22 | Framework (signal-first era) |
| @angular/material | ^22 | Componentes UI |
| @angular/cdk | ^22 | Utilities (layout, overlay, etc.) |
| ng2-charts | ^7 | Wrapper de Chart.js para Angular |
| chart.js | ^4 | Gráficos |
| @angular/animations | ^22 | Transiciones Material |

### Dev
| Paquete | Uso |
|---------|-----|
| vitest | Tests unitarios |
| cypress | E2E tests |
| eslint + prettier | Linting y formato |

---

## 5. Plan de Migración por Fases

### Fase 1: Scaffolding y Layout (1-2 días)
- [ ] **Mockups de navegación** — Elaborar propuestas visuales de layout de menú con pros/contras:
  - Opción A: Barra superior con tabs (estilo actual mejorado con Material)
  - Opción B: Sidebar lateral colapsable (estilo dashboard/admin panel)
  - Opción C: Bottom navigation bar flotante (estilo app móvil)
  - Opción D: Barra superior con menú hamburguesa en móvil
  - Incluir: wireframes, responsive behaviour, y recomendación final
- [ ] Crear proyecto Angular con `ng new futmondo-angular --standalone`
- [ ] Instalar Angular Material con tema custom
- [ ] Crear shell layout según el mockup elegido
- [ ] Configurar proxy a backend (angular.json proxy o environment)

### Fase 2: Tab Presupuesto (1 día)
- [ ] Budget service (GET balances, GET detail, POST sync)
- [ ] Budget overview (mat-table con sort)
- [ ] Budget detail (tabla de altas/bajas)
- [ ] Money pipe y componente money-cell

### Fase 3: Tab Evolución (1 día)
- [ ] Evolution service
- [ ] Points chart (ng2-charts line chart)
- [ ] Positions chart (ng2-charts con eje invertido)
- [ ] Tooltip interactivo con foto de jugador

### Fase 4: Tabs Estadísticas + Finanzas + Clausulables (1-2 días)
- [ ] Stats con 3 gráficos de barras
- [ ] Finances table (premium)
- [ ] Clausulable table con sort (premium)

### Fase 5: Analytics Avanzado (2-3 días)
- [ ] Sub-routing con tabs secundarios
- [ ] 7 secciones con sus componentes (sin humor)
- [ ] Clasificación dinámica con controles interactivos

### Fase 6: Pulido (1 día)
- [ ] Transiciones y animaciones
- [ ] Responsive final
- [ ] Tests básicos

### Total estimado: 6-9 días

---

## 6. Configuración del Proxy (desarrollo)

```json
// proxy.conf.json
{
  "/api": {
    "target": "http://localhost:8001",
    "secure": false,
    "changeOrigin": true
  }
}
```

En producción se puede desplegar el frontend estático (ng build) y servir con nginx/caddy con proxy pass a la API.

---

## 7. Tema Material Custom

```scss
// styles.scss
@use '@angular/material' as mat;

$futmondo-primary: mat.m2-define-palette(mat.$m2-green-palette, 500, 300, 700);
$futmondo-accent: mat.m2-define-palette(mat.$m2-deep-purple-palette, A200, A100, A400);
$futmondo-warn: mat.m2-define-palette(mat.$m2-red-palette);

$futmondo-theme: mat.m2-define-light-theme((
  color: (
    primary: $futmondo-primary,
    accent: $futmondo-accent,
    warn: $futmondo-warn,
  ),
  typography: mat.m2-define-typography-config(),
));

@include mat.all-component-themes($futmondo-theme);

// Custom utilities
.money-positive { color: #16a34a; font-weight: 600; }
.money-negative { color: #dc2626; font-weight: 600; }
.clickable { cursor: pointer; &:hover { background: rgba(0,0,0,0.04); } }
```
