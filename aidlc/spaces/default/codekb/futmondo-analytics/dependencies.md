# Dependencias — futmondo-analytics

## Dependencias Externas

Las versiones concretas de librerías están en `technology-stack.md`; aquí se documentan los
servicios y relaciones de dependencia, no se repite la tabla de versiones.

### Servicios externos (runtime)

- **API Futmondo** — fuente autoritativa de datos de fantasy y destino de las pujas
  (`POST {base_url}/1/market/bid`). Consumida por `backend-app-services`
  (`futmondo_client.py`) con credenciales por usuario resueltas en `_helpers`. **El cálculo
  de premios (`sync_prizes`) depende fuertemente de esta API** (standings, rounds,
  round_ranking, dream_team, round_lineup, round_matches) con `time.sleep()` entre llamadas.
  **Modo de fallo actual (FR4)**: el cliente traga `Timeout`/`RequestException`/
  `JSONDecodeError` y devuelve `None`; el fallo se propaga como ausencia de datos, no como
  excepción tipada. Ver `code-quality-assessment.md`.
- **API Sofascore** — ratings de jugadores, consumida por `sofascore_client.py` vía
  `curl_cffi`. **Modo de fallo (patrón de referencia)**: distingue `SofascoreIPBanError`
  (fatal, re-lanzado) del 404 recuperable (`None`).
- **Neon PostgreSQL** (Frankfurt, free) — persistencia productiva; usada por
  `backend-app-stores` y por `backend-app-auth` (SQL crudo directo), a través de
  `db_connection` (pool `ThreadedConnectionPool` 5-20 con rollback+raise y retry x3). Aloja
  la tabla `team_prizes` (fuente de verdad de premios), `user_championships` (config de
  premios), la caché de sync y las tablas de tareas/sesiones durables. Fallback SQLite/Turso.

### Plataforma / build / entrega

- **Fly.io** — hosting de `futmondo-api` y `futmondo-app`; crons one-shot (disparan el sync
  que ejecuta el worker `data_sync_service`).
- **GitHub Actions** — CI/CD (gitleaks, pytest, ng test, deploy). Ver
  `code-quality-assessment.md`.
- **npm registry** — dependencias del frontend (`@angular/*`, `vitest`, `jsdom`, `chart.js`,
  `ng2-charts`, `marked`). Restauradas con `npm ci` en ambos workflows.

## Dependencias del Frontend

Detalle de versiones en `technology-stack.md`. Relaciones de dependencia relevantes:

- **`angular-app` runtime** → `@angular/*` (^22.1.0), `chart.js`/`ng2-charts` (gráficos),
  `marked` (assistant), `rxjs`, `tslib`. Todas OSS, coste 0 €.
- **`angular-app` build/test** → `@angular/build` (^22.1.2, builder esbuild/vite),
  `@angular/cli` (^22.1.2), `@angular/compiler-cli` (^22.1.0), `vitest` (^4.0.8) + `jsdom`
  (^25.0.1) para `ng test` vía `@angular/build:unit-test`, `typescript` (~6.0.2), `prettier`
  (^3.8.1). El estado de la infraestructura de cobertura del frontend (evolucionada en un
  intent previo) vive en `code-quality-assessment.md`.

## Dependencias de CI/CD

- **`ci.yml`** (PR→`main`) depende de: acción de gitleaks (BLOQUEANTE), Python 3.12 +
  `backend/requirements.txt` (`pytest --cov=app`), Node `'22'` + `npm ci` en `angular-app`
  (`ng test --watch=false` BLOQUEANTE). `ruff`, `pip-audit`, `ng lint`, `npm audit` advisory.
- **`fly-deploy.yml`** (push→`main`) depende de: gitleaks@v2 (BLOQUEANTE), `pytest -q` **sin
  `--cov`** (BLOQUEANTE), Node `'22'` + `npm ci` + `ng test --watch=false` (BLOQUEANTE); y de
  `flyctl` + tokens Fly.io para `deploy-backend`/`deploy-frontend` y el `smoke-test` a
  `/health`.
- **`daily-sync.yml` / `sofascore-sync.yml`** dependen de la imagen cron (`cron-worker`) y de
  `flyctl` para crear/ejecutar/destruir máquinas Fly one-shot.

## Dependencias Internas (cross-package)

Resumen del grafo (detalle por componente en `component-inventory.md`):

```mermaid
graph LR
    angular["angular-app"] --> proxy["proxy-nginx"]
    proxy --> main["backend-app-main"]
    main --> auth["backend-app-auth"]
    main --> endpoints["backend-app-api-endpoints"]
    main --> core["backend-app-core"]
    main --> services["backend-app-services"]
    main --> stores["backend-app-stores"]
    endpoints --> auth
    endpoints --> services
    endpoints --> stores
    auth --> stores
    auth --> services
    services --> stores
    security["backend-app-security"] --> core
    cron["cron-worker"] --> services
    ci["ci-workflow"] --> angular
    ci --> backendpkg["backend"]
    fd["fly-deploy-workflow"] --> angular
    fd --> backendpkg
```

<!-- Text fallback: angular-app depende de proxy-nginx, que depende de backend-app-main. main depende de auth, api-endpoints, core, services y stores. api-endpoints depende de auth, services y stores. auth depende de stores y services. services depende de stores. security depende de core. cron-worker depende de services. Los workflows ci-workflow y fly-deploy-workflow dependen del build/test de angular-app y del backend. -->

## Notas de Dependencias Relevantes al Área de Fiabilidad (intent activo)

- **Acoplamiento del worker de sync**: `data_sync_service` (god-file) depende de
  `db_connection` (conexión/pool), `futmondo_client` y `sofascore_client` (clientes
  externos) y `data_manager_v2` (persistencia). El **contrato de fallo NO es uniforme**:
  Sofascore expone excepción tipada, Futmondo colapsa a `None`, `db_connection` re-lanza. Un
  cambio de contrato en `futmondo_client` (introducir excepción tipada, FR4) tiene **blast
  radius alto** en el god-file de sync: los getters `get_*` devuelven `Optional` y los
  `sync_*` asumen `None == sin datos`. Hay que mapear los llamadores antes de cambiar el
  contrato.
- **Acoplamiento de durabilidad de tareas**: `task_service` (autoridad = `task_repository` en
  `stores/`) depende de `task_manager` como caché best-effort. El patrón
  autoridad-vs-best-effort de `_cache_call` es la referencia interna para clasificar fallos.
- **Punto de corromper-datos**: el bloque de premios en `data_sync_service` acopla
  `commit()` (L1825) con un `DELETE ... NOT IN` posterior (L1846) cuyo fallo se traga
  (L1859). La caracterización previa a cualquier cambio exige dobles/fakes en memoria
  (patrón `conftest.py`), coste 0 €.
- **Coste 0 €**: cualquier dependencia nueva debe sostenerse en tiers gratuitos.

## Notas de Dependencias Relevantes al Área de Premios

- **Acoplamiento de escritura de premios**: la fórmula (`data_sync_service.sync_prizes`)
  acopla el cálculo a la API de Futmondo y a la BD (`team_prizes`, `user_championships`) en
  un mismo god-file, sin capa repositorio. La caracterización previa al refactor exige
  **dobles/fakes** de la API de Futmondo y de la capa de persistencia.
- **Acoplamiento de lectura**: `player_finances` y `balances` dependen de `team_prizes` vía
  `DataManagerV2` (`get_prizes_by_team`); `player_finances` además resuelve identidad por
  team_id/user_id/nombre (frágil, ver `code-quality-assessment.md`).

## Notas de Dependencias Relevantes a Intents Anteriores (security)

- **FR8**: `SSL_VERIFY=0` está declarado en `docker-compose.yml` pero ningún módulo Python lo
  consume (grep sobre `backend/**` = 0 usos); `verify=` en `futmondo_client.py` no lo lee. El
  flag es una dependencia de configuración huérfana y ausente de `backend/fly.toml [env]`.
- **FR9**: `backend-app-auth` depende directamente de Neon PostgreSQL con SQL crudo; el tipo
  de `expires_at` (aware en PostgreSQL vía `.isoformat()` con offset) es el que dispara el
  bug de precedencia. Evidencia en `code-quality-assessment.md`.
