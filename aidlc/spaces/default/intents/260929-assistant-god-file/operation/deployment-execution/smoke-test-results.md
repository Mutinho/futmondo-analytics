# Smoke Test Results — refactor DDD del asistente

Intent `260929-assistant-god-file`, scope `refactor`. Registra la verificación de smoke test del
despliegue: el equivalente ejecutable pre-merge y el smoke test post-deploy que corre on-merge.

## Smoke test de release (post-deploy, on-merge)

- **Definición**: job `smoke-test` de `fly-deploy.yml` — `curl` a `${SMOKE_HEALTH_URL:-https://futmondo-api.fly.dev/health}`,
  5 reintentos con 10 s de espera, éxito si HTTP 200.
- **Estado**: **PENDIENTE** — se ejecuta cuando el usuario fusione a `main` y el pipeline despliegue.
  No lo ejecuta el agente (el código aún no está fusionado y el despliegue es on-merge).
- **Criterio de éxito esperado**: `GET /health` → HTTP 200 con `{"status":"healthy"}`.

## Verificación equivalente pre-merge (ejecutada localmente)

Como el refactor preserva la superficie pública, el arranque del servicio y la salud del endpoint se
verifican indirectamente pre-merge sin desplegar:

| Verificación | Comando | Resultado |
|--------------|---------|-----------|
| Import histórico del endpoint | `python -c "from app.services.assistant_service import get_assistant_service; get_assistant_service()"` | OK (ask/usage_tracker/_save_market_to_db presentes) |
| Suite de tests (arranque + comportamiento) | `pytest --cov=app -q` (desde `backend/`) | 244 passed, 3 xfailed; cobertura 33.82% ≥ 27 |
| Tests del asistente unit-scoped | `pytest tests/test_assistant_*.py -q` | 26 passed |

Estas verificaciones congelan que el paquete refactorizado arranca e integra igual que el god-file
previo; el smoke `/health` post-deploy confirmará la salud en producción tras el merge.

## Interpretación

- El artefacto desplegado (app FastAPI con el paquete DDD nuevo tras el shim) es funcionalmente
  equivalente al previo. El smoke test post-deploy es la verificación de release definitiva; su
  ejecución queda registrada como pendiente del merge.
