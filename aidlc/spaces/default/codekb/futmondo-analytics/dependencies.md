# Dependencias — futmondo-analytics

## Dependencias Externas

Las versiones concretas de librerías están en `technology-stack.md`; aquí se documentan los
servicios y relaciones de dependencia, no se repite la tabla de versiones.

### Servicios externos (runtime)

- **API Futmondo** — fuente autoritativa de datos de fantasy y destino de las pujas
  (`POST {base_url}/1/market/bid`). Consumida por `backend-app-services`
  (`futmondo_client.py`) con credenciales por usuario resueltas en `_helpers`.
- **API Sofascore** — ratings de jugadores, consumida por `sofascore_client.py` vía
  `curl_cffi`.
- **Neon PostgreSQL** (Frankfurt, free) — persistencia productiva; usada por
  `backend-app-stores` y por `backend-app-auth` (SQL crudo directo). Fallback SQLite/Turso.

### Plataforma / build

- **Fly.io** — hosting de `futmondo-api` y `futmondo-app`; crons one-shot.
- **GitHub Actions** — CI/CD (gitleaks, pytest, ng test, deploy). Ver
  `code-quality-assessment.md`.

## Dependencias Internas (cross-package)

Resumen del grafo (detalle por componente en `component-inventory.md`):

```mermaid
graph LR
    angular["angular-app"] --> proxy["proxy-nginx"]
    proxy --> main["backend-app-main"]
    main --> auth["backend-app-auth"]
    main --> endpoints["backend-app-api-endpoints"]
    main --> core["backend-app-core"]
    endpoints --> auth
    endpoints --> services["backend-app-services"]
    endpoints --> stores["backend-app-stores"]
    auth --> stores
    auth --> services
    services --> stores
    security["backend-app-security"] --> core
    cron["cron-worker"] --> services
```

<!-- Text fallback: angular-app depende de proxy-nginx, que depende de backend-app-main. main depende de auth, api-endpoints y core. api-endpoints depende de auth, services y stores. auth depende de stores y services. services depende de stores. security depende de core. cron-worker depende de services. -->

## Notas de Dependencias Relevantes al Intent

- **FR8**: `SSL_VERIFY=0` está declarado en `docker-compose.yml` pero ningún módulo Python lo
  consume (grep sobre `backend/**` = 0 usos); `verify=` en `futmondo_client.py` no lo lee. El
  flag es una dependencia de configuración huérfana y ausente de `backend/fly.toml [env]`.
- **FR9**: `backend-app-auth` depende directamente de Neon PostgreSQL con SQL crudo; el tipo
  de `expires_at` (aware en PostgreSQL vía `.isoformat()` con offset) es el que dispara el
  bug de precedencia. Evidencia en `code-quality-assessment.md`.
- **Coste 0 €**: cualquier dependencia nueva debe sostenerse en tiers gratuitos.
