# Smoke Test Results — F1: Login nativo end-to-end

> Fase: operación (deployment-execution). Idioma: castellano; tokens técnicos verbatim en inglés.
> El smoke test del backend es la verificación de release (no hay staging). El "smoke" de la app
> iOS es la validación manual del flujo F1 en el dispositivo.

## Smoke test del backend (automático en el CD)

| Comprobación | Método | Resultado |
|--------------|--------|-----------|
| `/health` responde 200 | `smoke-test` job de `fly-deploy.yml`: `curl` a `https://futmondo-api.fly.dev/health` (hasta 5 reintentos, HTTP 200) | ✅ PASS (parte del release de D-01) |

Verificación en vivo adicional (desde el entorno del agente, 2026-10-18):

```
$ curl -sS -w "HTTP %{http_code} time=%{time_total}s\n" https://futmondo-api.fly.dev/health
HTTP 200 time=0.47s
{"status":"healthy"}
```

## Smoke funcional de F1 contra prod (endpoints de auth)

El transporte de D-01 se ejercitó end-to-end desde la app nativa contra el backend prod:

| Flujo | Qué valida | Resultado |
|-------|------------|-----------|
| Login nativo | `POST /auth/login` devuelve `refresh_token` en el body (nuevo canal de D-01) + access token; la app lo guarda en Keychain | ✅ PASS (login correcto en el iPhone) |
| Auto-login al reabrir | la app recupera el refresh token del Keychain y renueva sesión sin re-login | ✅ PASS (sesión recuperada tras cerrar/reabrir) |
| Logout | revoca la sesión y limpia el Keychain | ✅ PASS |
| Retrocompatibilidad PWA | la PWA (cookie `HttpOnly`) sigue funcionando; ignora el `refresh_token` del body | ✅ sin regresión (precedencia cookie primero) |

## Observaciones

- No hay suite E2E automatizada de dispositivo (deuda P-1 del arnés iOS): el smoke de la app es
  manual, ejecutado por el propietario en el iPhone 13 Pro. Documentado como deuda, no bloquea F1.
- Los 8 tests de transporte del backend (`test_auth_refresh_transport.py`) cubren la precedencia
  cookie → header → body en el gate de CI; el smoke en vivo confirma el comportamiento en prod.

## Sources

- [consumes] deployment-log.md; cd-config.md, deployment-strategy.md; test-results.md.
- [code] `.github/workflows/fly-deploy.yml` (job `smoke-test`); verificación en vivo `curl /health`.
- [memory] team.md `## Deployment` (smoke `/health` como verificación de release);
  aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
