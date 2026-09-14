# Resultados de Smoke Test — Mejoras de CI/Tooling

> Etapa Deployment Execution (Operation) · Intent `260914-ci-tooling-mejoras` · Scope `refactor`.
> Los smoke tests de despliegue los ejecuta el pipeline `fly-deploy.yml` tras el deploy. Aquí se registra el diseño del smoke test y la verificación local disponible.

## Smoke test del pipeline (post-deploy)

Definido en `fly-deploy.yml` job `smoke-test`:

```bash
URL="${SMOKE_HEALTH_URL:-https://futmondo-api.fly.dev/health}"
for i in 1 2 3 4 5; do
  code=$(curl -s -o /tmp/health.json -w "%{http_code}" "$URL")
  [ "$code" = "200" ] && exit 0
  sleep 10
done
exit 1   # /health no devolvió 200
```

| Check | Objetivo | Cuándo | Estado |
|-------|----------|--------|--------|
| Backend `/health` | HTTP 200 (5 reintentos) | Tras deploy backend+frontend | Pendiente (lo ejecuta el pipeline al hacer push a `main`) |
| Frontend `/` | HTTP 200 (health check Fly.io) | Continuo (fly.toml `[checks.health]`) | Pendiente (post-deploy) |

## Verificación local disponible en esta sesión

Como el despliegue no se dispara desde aquí, el smoke test contra producción no aplica en esta sesión. La verificación equivalente realizada:

| Verificación | Resultado |
|--------------|-----------|
| Tests frontend (Vitest, contenedor node:22.22.3) | 6/6 verdes |
| `npm ci` | Limpio, 0 vulnerabilidades, sin Karma |
| Coherencia de workflows (setup-node@v5, sin Chrome, sin flag inseguro) | OK (inspección) |

## Conclusión

El smoke test real (`/health`) se ejecutará en el pipeline al integrar a `main`. La no regresión funcional del intent está verificada localmente (tests verdes). Ningún cambio del intent afecta a endpoints de la app (NFR2).
