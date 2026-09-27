# Resultados del Smoke Test — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, brownfield. Conversation language: Spanish.

## Definición del smoke test (pipeline)

Job `smoke-test` de `.github/workflows/fly-deploy.yml`:

- Target: `GET ${SMOKE_HEALTH_URL:-https://futmondo-api.fly.dev/health}`.
- Éxito: HTTP 200 en cualquiera de 5 reintentos (sleep 10 s entre intentos).
- Fallo: si `/health` no devuelve 200 tras 5 intentos, el job queda en rojo (release marcado como fallido → señal de rollback).

## Cobertura del cambio por el smoke test

- La extracción de `analytics` vive en el backend (`futmondo-api`), la misma app que responde `/health`. Si el paquete no importara (p. ej. un error en el shim), el arranque de FastAPI fallaría y `/health` no devolvería 200 → el smoke test lo detectaría.
- Verificación local equivalente ya realizada: `python -c "import app.main"` resuelve sin error y la suite pasa (218/0).

## Resultado

- **Local (pre-merge)**: la app importa y arranca; suite verde. Equivalente funcional al arranque que valida el smoke test.
- **Producción**: PENDIENTE — el smoke test `/health` se ejecutará automáticamente tras el `deploy-backend` cuando el cambio se fusione a `main`. No se ha ejecutado contra producción porque el cambio aún no se ha desplegado.

## Nota

No se ejecuta `curl` contra el `/health` de producción en este stage porque desplegaría/validaría un estado que aún no incluye la extracción; la verificación autoritativa es la del pipeline post-merge.
