# Smoke Test Results — Durabilidad del estado

> Etapa Deployment Execution (Operation). **Criterios de smoke test planificados.** El smoke test se
> ejecuta dentro del pipeline `fly-deploy.yml` tras el deploy (al fusionar a `main`); no se ejecutó
> desde el workflow porque el despliegue aún no ha ocurrido. Este documento fija los criterios y el
> resultado esperado.

## Estado

- **Estado**: PLANIFICADO — se ejecutará en el job `smoke-test` de `fly-deploy.yml` tras el deploy.

## Smoke test del pipeline (existente)

| Ítem | Valor |
|------|-------|
| Endpoint | `https://futmondo-api.fly.dev/health` (o `SMOKE_HEALTH_URL`) |
| Método | `curl` HTTP GET |
| Reintentos | 5 (con `sleep 10` entre intentos) |
| Criterio de éxito | HTTP 200 |
| Fallo | Si `/health` no devuelve 200 tras 5 intentos → job falla → deploy considerado fallido |

## Verificaciones específicas de durabilidad (recomendadas tras el deploy)

Además del smoke test automático `/health`, comprobaciones manuales recomendadas para confirmar el
beneficio de la durabilidad (no bloquean el pipeline; validación de operador):

| Verificación | Cómo | Resultado esperado |
|--------------|------|--------------------|
| Sesión sobrevive a reinicio (FR1.2) | Login → `fly apps restart futmondo-api` → primera petición autenticada | La sesión se rehidrata sin re-login (con `FUTMONDO_CRED_KEY` fijado) |
| Sin secret → degradación segura (FR1.3) | (Solo si el secret no está fijado) primera petición tras reinicio | 401 accionable, NO 403 opaco |
| Tarea consultable tras reinicio (FR1.4) | Lanzar sync → reinicio → `GET /api/v1/sync/task/{id}` | Devuelve último estado conocido |
| Tarea en curso marcada al reinicio (FR1.5) | Reinicio con tarea en curso | Estado `interrupted_by_restart`, no "en curso" indefinido |

## Resultado

- Pendiente de ejecución en el pipeline al fusionar a `main`. El criterio bloqueante es el smoke test
  `/health` = 200; las verificaciones de durabilidad son validación de operador post-deploy.
