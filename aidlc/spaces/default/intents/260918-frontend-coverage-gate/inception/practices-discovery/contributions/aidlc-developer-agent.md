**Collaborator:** aidlc-developer-agent

## Contribution

Inspección ciega del borrador del lead desde la lente DEVELOPER (naming, límites de
capa, manejo de errores, organización de ficheros, code-style y la **mecánica** de
añadir infra de tests/cobertura al frontend sin reescrituras). El borrador es sólido y
coincide con la evidencia del código; señalo confirmaciones y **dos correcciones
mecánicas de peso** que la entrevista DEBE resolver, más matices de ergonomía.

### 1. FR10.1 — retirada de `skipTests: true` en `angular.json`

Evidencia (`angular-app/angular.json`): `skipTests: true` está en los **8** schematics
(`component`, `class`, `directive`, `guard`, `interceptor`, `pipe`, `resolver`,
`service`). Recomendación de developer, **de grano fino** (no "todos o ninguno"):

- **Retirar `skipTests`** de los schematics de lógica con valor de test real:
  `service`, `guard`, `interceptor`, `class`, `component`. Es donde vive el
  comportamiento (HTTP, auth/refresh, estado con signals) y donde la ergonomía de
  "nace con spec" paga.
- **Conservar `skipTests: true`** (o dejarlo a criterio) en `pipe`, `resolver`,
  `directive`: en este repo hay 1 pipe trivial (`money.pipe.ts`, 589 B) y no hay
  resolvers; forzar spec en generadores triviales produce specs vacíos de valor y roza
  el anti-patrón `assert True` que la fase de construcción prohíbe. Un pipe SÍ se
  testea cuando tiene lógica; el flag solo cambia el default del generador, no impide
  crear el spec a mano cuando haga falta.
- Matiz de ergonomía: retirar el flag **no** genera specs retroactivos; solo afecta a
  ficheros NUEVOS. La deuda de los ~69 ficheros sin spec se cubre por la **siembra**
  (fase 1), no por este flag. Conviene decirlo explícito para no crear la expectativa
  de que quitar el flag sube la cobertura por sí solo.

### 2. CORRECCIÓN MECÁNICA — dónde vive la config de cobertura (NO es `vitest.config`)

El borrador (Testing Posture fase 3, Code Style, y `discovered-rules.md`) afirma repetidamente
crear un **`vitest.config`** con `coverage.provider` + `coverage.thresholds`. Esto es
**inexacto para este stack** y la entrevista debe corregirlo antes de afirmarlo como regla:

- El proyecto NO usa Vitest directamente; usa el builder **`@angular/build:unit-test`**
  con `runner: vitest` (`angular.json` → `architect.test`). En ese builder, la
  configuración de cobertura (`codeCoverage`, y en su caso umbrales) se declara en las
  **`options` del target `test` de `angular.json`**, no en un `vitest.config.ts` suelto
  que el builder podría ignorar. Un `vitest.config` "a mano" es frágil: puede quedar
  fuera del flujo del builder o pisar sus defaults.
- Acción segura: (a) **confirmar en la entrevista** dónde soporta el builder de Angular 22
  declarar `coverage`/umbrales (target `test` en `angular.json` y/o el flag de
  `ng test` para cobertura), y (b) reescribir la regla candidata "el umbral vive en
  `vitest.config`" como "el umbral vive en la **config del target `test` de
  `angular.json`** (fuente única)". Mantener el espíritu del borrador (config única,
  no dispersa) pero con el fichero correcto. Sin esto, la fase 3 arriesga tiempo
  peleando con un `vitest.config` que el builder no lee.
- Consecuencia sobre FR17.1: si la cobertura y el umbral se activan **dentro de
  `ng test`** (vía el target/flag del builder), la herencia a `ci.yml` y a `verify` que
  describe el borrador SÍ se sostiene, porque ambos ya corren `ng test --watch=false`.
  Pero eso EXIGE que el `ng test` de CI pase el flag de cobertura (p. ej.
  `ng test --coverage --watch=false` o el equivalente del builder) — hoy corren `ng test
  --watch=false` **sin** cobertura. La entrevista debe fijar el comando exacto en ambos
  workflows; "hereda automáticamente" es cierto solo si el flag de cobertura queda
  cableado en el comando o como default del target.

### 3. Ergonomía de specs — patrón existente a replicar (confirmado)

Los 2 specs existentes fijan un patrón limpio y reproducible que la siembra debe seguir
al pie de la letra:

- `auth.interceptor.spec.ts`: `TestBed.configureTestingModule` con
  `provideHttpClient(withInterceptors([...]))` + `provideHttpClientTesting()`, mock de
  `AuthService` por `{ provide: AuthService, useValue: ... }` con `vi.fn()`, y
  `HttpTestingController.expectOne(...).flush(...)` + `httpMock.verify()` en `afterEach`.
  Es exactamente el harness que necesitan los servicios HTTP y el interceptor.
- `idle-preloading-strategy.spec.ts`: clase pura instanciada con `new`, `vi.useFakeTimers()`
  para el tiempo. Patrón directo para cualquier lógica con temporizadores.
- Import style: named imports de `vitest` (`describe/it/expect/vi/...`) y de
  `@angular/*/testing`; docstrings de caracterización en castellano con trazas a FR/BR
  (coherente con Code Style del borrador). La siembra debe conservar este estilo.

### 4. Orden de siembra — factibilidad por dificultad de harness (confirmado y afinado)

Priorización desde DI-friendliness real del código leído:

- **Más fáciles (thin HTTP wrappers, `providedIn: 'root'`, `firstValueFrom`)**: sembrar
  primero. `budget.service.ts`, `sync.service.ts` (salvo `syncWithPolling`),
  `championship.service.ts`, `stats.service.ts`, `evolution.service.ts`,
  `roster.service.ts`, `favorites.service.ts`, `analytics.service.ts`,
  `assistant.service.ts`. Todos se testean con el harness `HttpTestingController` del
  interceptor. Alto valor/cobertura por bajo coste.
- **Fácil con matiz de tiempo/estado**: `auth.service.ts` (signals + `localStorage` +
  `Router`): mockear `Router` por `useValue`, y `localStorage` (jsdom lo trae, pero
  aislar y limpiar por test). `sync.service.ts::syncWithPolling` usa un `delay` con
  `setTimeout` privado → **fake timers**, como el preloading spec.
- **Fácil pero requiere contexto de inyección**: `core/guards/auth.guard.ts`. Es una
  `CanActivateFn` que usa `inject()`; invocarla dentro de
  `TestBed.runInInjectionContext(() => authGuard(...))` con `AuthService` y `Router`
  mockeados. Cubre la rama de recuperación de sesión (`tryRecoverSession`) y el
  `navigate(['/login'])`. Alto valor transversal; recomiendo incluirlo en fase 1.
- **Más pesados (dejar fuera de fase 1 salvo decisión explícita)**: componentes de
  `features/*` (standalone + Material + Chart.js + diálogos) necesitan harness más
  caro (`provideNoopAnimations`, mocks de `MatDialog`, `provideRouter`). `bid-dialog`
  (FR6) es candidato razonable si el humano lo pide, pero encarece la fase 1; mejor
  diferir a rondas posteriores del trinquete.

### 5. Disciplina de devDependencies (confirmo como Mandated)

Añadir `@vitest/coverage-v8` cambia `package.json` + `package-lock.json`
(`devDependencies` actuales confirmadas: sin proveedor de cobertura). La regla ya
afirmada — verificar `npm ci` + `ng test` en local o contenedor `node:22.22.3`
(= `.nvmrc`, `packageManager: npm@11.12.1`) antes de pushear — **aplica de lleno** y
debe seguir como Mandated. El proveedor debe ser OSS/coste 0 € (`@vitest/coverage-v8`
lo es y es el nativo del runner Vitest ya en uso → menos fricción que `istanbul`).
Añado: verificar que `@vitest/coverage-v8` case en versión con `vitest ^4.0.8`
(mismatch de major entre vitest y su provider rompe la instrumentación).

### 6. Límites de capa / code-style (sin fricción; una nota)

- La organización actual (`core/services`, `core/guards`, `core/interceptors`,
  `core/preloading`, `features/*`, `shared/*`) es limpia y feature-oriented; los specs
  co-locados `*.spec.ts` respetan `tsconfig.spec.json` (`include: src/**/*.spec.ts`). El
  borrador acierta al no introducir un árbol de tests separado.
- Nota brownfield: la regla afirmada de NO correr `ruff format` masivo es backend; su
  equivalente frontend sería no reformatear en masa ficheros existentes con
  Prettier/ESLint al sembrar specs — formatear solo los ficheros nuevos, para no inflar
  diffs ni invalidar el pase de revisión. Sugiero que la entrevista confirme este matiz
  explícitamente para el frontend (hoy solo está escrito para backend/`ruff`).

## Positions

AGREE: FR10 → FR17.1 es el orden correcto; activar cobertura dentro de `ng test` propaga el gate a `ci.yml` y `verify` sin duplicar config.
AGREE: umbral como trinquete (solo sube) partiendo de un piso que la línea base ya supere; medir tras la siembra antes de fijar el valor.
AGREE: siembra de `core/services/*` + `auth.guard.ts` + interceptor antes de subir el umbral; son las piezas más DI-friendly y de mayor valor transversal.
AGREE: `@vitest/coverage-v8` (OSS, nativo del runner ya en uso) y la disciplina Mandated de verificar `npm ci` + `ng test` en `node:22.22.3` tras tocar devDependencies.
AGREE: specs co-locados `*.spec.ts` replicando el patrón `TestBed` + `provideHttpClient(withInterceptors)` + `provideHttpClientTesting` de los 2 specs existentes.
OBJECT: el borrador ubica el umbral/proveedor en un `vitest.config`; en este stack la cobertura se declara en las `options` del target `test` de `angular.json` (builder `@angular/build:unit-test`). La entrevista DEBE fijar el fichero correcto o la fase 3 pelea con una config que el builder podría ignorar.
OBJECT: "los caminos que corren `ng test` heredan la cobertura automáticamente" solo es cierto si el comando pasa el flag de cobertura; hoy `ci.yml` y `verify` corren `ng test --watch=false` SIN cobertura. La entrevista debe fijar el comando exacto (p. ej. flag `--coverage`/equivalente) en ambos workflows.
OBJECT: retirar `skipTests` de TODOS los schematics es subóptimo; conservarlo en `pipe`/`resolver`/`directive` evita forzar specs triviales (anti-patrón `assert True`). Retirarlo en `service`/`guard`/`interceptor`/`class`/`component`.
