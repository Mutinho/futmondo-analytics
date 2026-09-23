# Resultados de smoke test — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. El smoke test lo ejecuta el
> job `smoke-test` de `fly-deploy.yml` **tras el deploy on-merge**. Este intent
> aún no está fusionado: se documenta el smoke test que se ejecutará y su
> criterio de éxito. Coste 0 €.

## Smoke test definido (verificación de release, NFR2.2)

- **Endpoint**: `GET https://futmondo-api.fly.dev/health` (o `vars.SMOKE_HEALTH_URL`).
- **Reintentos**: hasta 5, con espera de 10 s entre intentos.
- **Criterio de éxito**: HTTP **200** → release sano; el job sale 0. Si tras 5
  intentos no hay 200, el job falla (exit 1) y el release se marca en rojo
  (disparador de rollback).

## Estado

- **Pendiente de merge**: el smoke test se ejecutará automáticamente al fusionar
  este intent a `main` y desplegar. No se dispara manualmente desde esta etapa.

## Cobertura funcional del smoke test respecto al intent

- El smoke test verifica la **disponibilidad** del backend (`/health` 200), que
  es la señal de release. Los cambios de este intent (estado `degraded`, techo de
  `price`, `except` acotados) no alteran el contrato de `/health`.
- La **corrección funcional** del intent está cubierta por la suite `pytest`
  (166 tests, gate bloqueante), no por el smoke test: el smoke test confirma que
  el servicio arranca y responde tras el deploy.

## Verificación local equivalente (coste 0 €, opcional pre-merge)

```bash
# Tras un deploy o en local con la app levantada:
curl -sS https://futmondo-api.fly.dev/health   # esperado: HTTP 200 {"status":"healthy"}
```

## Sources

- `.github/workflows/fly-deploy.yml` (job `smoke-test`),
  `operation/deployment-pipeline/deployment-strategy.md`, `deployment-log.md`.

## Assumptions & Open Questions

None.
