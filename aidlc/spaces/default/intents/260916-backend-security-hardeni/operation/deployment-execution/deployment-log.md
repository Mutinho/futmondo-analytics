# Registro de Ejecución del Despliegue — Backend Security Hardening

> Scope `security-patch`, fase Operation, brownfield. Documenta cómo se ejecuta
> el despliegue de este release de seguridad. Perspectivas integradas (inline):
> ingeniería de release + desarrollo (migraciones de BD). Stack real: Fly.io +
> Neon, coste 0 €.

## Modelo de ejecución

El despliegue se dispara **on-merge a `main`** vía el pipeline existente
`.github/workflows/fly-deploy.yml`. No se ejecuta un `fly deploy` manual desde
esta etapa: el merge del MR (tras pasar el gate de CI bloqueante) es el
disparador. Un solo entorno, sin staging separado.

### Secuencia de jobs (encadenados por `needs:`)

1. `verify` — gitleaks (bloqueante) + `pytest -q` (Python 3.12) + `ng test`
   (Node 22). Un rojo aquí aborta el despliegue.
2. `deploy-backend` — `flyctl deploy ./backend` → app `futmondo-api`.
3. `deploy-frontend` — `flyctl deploy ./angular-app` → app `futmondo-app`.
4. `smoke-test` — `curl` a `/health`, 5 reintentos esperando HTTP 200.

## Contenido de este release

Cinco correcciones de seguridad (cambios de código Python + tests, y una
edición de `docker-compose.yml` solo-local):

| FR | Cambio | Riesgo de despliegue |
|----|--------|----------------------|
| FR6 | Validación `price<=0` en `place_bid` | Bajo |
| FR7 | Protección de `/api/v1/photos` | Bajo |
| FR8 | Eliminar `SSL_VERIFY=0` (solo `docker-compose.yml` local) | Nulo en prod |
| FR9 | Corrección de precedencia en `is_refresh_token_valid` | Bajo-medio (auth) |
| FR18 | Guarda de endpoints admin de BD (`ENABLE_DB_ADMIN`) | Bajo |

## Migraciones de base de datos

**Ninguna.** Verificado con la perspectiva de desarrollo contra `test-results.md`
y `code-summary.md`: ninguna de las cinco correcciones altera el esquema de Neon.
No hay pasos expand/contract, ni backfill, ni scripts de migración. No se delega
ejecución de migración al desarrollador porque no aplica.

## Precondiciones verificadas

- Build and Test: **135 passed, 0 fallos, 0 regresiones** (baseline 125 → +10).
- Secretos productivos vía GitHub Actions / Fly.io; el patch no introduce
  literales de secreto (gitleaks local sin hallazgos en los ficheros del patch).
- `environment-inventory` ausente por diseño (environment-provisioning se salta
  en `security-patch`); se usa la configuración real del pipeline y `fly.toml`.

## Estado

Listo para desplegar al fusionar el MR a `main`. La ejecución efectiva ocurre en
GitHub Actions/Fly.io en ese momento; este registro documenta el procedimiento y
sus precondiciones.
