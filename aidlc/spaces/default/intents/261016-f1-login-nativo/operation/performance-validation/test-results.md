# Performance Test Results — F1: Login nativo end-to-end

> Fase: operación (performance-validation). Idioma: castellano; tokens técnicos verbatim en inglés.
> Mediciones puntuales reales (herramienta gratuita `curl`), ejecutadas el 2026-10-18 contra prod
> (`https://futmondo-api.fly.dev`). No es un load test sostenido (NO-APLICA de pago); es evidencia
> de ausencia de regresión del transporte D-01.

## Mediciones (reales, 2026-10-18)

### `GET /health` (línea base del servidor)

| Muestra | HTTP | total | connect |
|---------|------|-------|---------|
| 1 (frío) | 200 | 0.450 s | 0.219 s |
| 2 | 200 | 0.212 s | 0.062 s |
| 3 (caliente) | 200 | 0.183 s | 0.058 s |

En caliente, el servidor responde en ~0.18 s; la primera muestra incluye el coste de establecer
conexión TLS.

### `POST /auth/login` (ruta de auth, credenciales inválidas)

| Muestra | HTTP | total | Nota |
|---------|------|-------|------|
| 1 | 401 | 0.416 s | Credencial inválida (sin secretos reales); la ruta valida contra la API de Futmondo |

El 401 es el camino esperado para credencial inválida (FR-1). La latencia de `/auth/login` está
dominada por el **round-trip a la API de Futmondo**, no por el transporte del refresh token de
D-01 (que es construcción/parsing de JSON, coste despreciable).

## Interpretación (ausencia de regresión de D-01)

- D-01 añade: (a) incluir `refresh_token` en el body de la respuesta de login, y (b) aceptar el
  token por body/header en refresh/logout. Ambas son operaciones de serialización/lectura en
  memoria; **no añaden I/O ni latencia material**.
- El `smoke-test` `/health` del release de D-01 ya pasó (HTTP 200), y las mediciones de arriba
  confirman tiempos normales tras el despliegue.

## Cliente nativo (iOS)

- El rendimiento percibido en la app (login → auto-login → logout) se validó manualmente en el
  iPhone 13 Pro como fluido; no hay harness de performance de dispositivo (deuda P-1, no bloquea
  F1).

## No ejecutado (NO-APLICA) y por qué

| Prueba | Estado |
|--------|--------|
| Load test sostenido / stress / soak | NO-APLICA (generador gestionado de pago; sin patrón de tráfico alto) |
| Validación de autoescalado | NO-APLICA (sin autoescalado configurado; entorno único) |
| Percentiles p95/p99 con métricas gestionadas | NO-APLICA (de pago) |

## Sources

- [consumes] load-test-plan.md; dashboards.md.
- [code] mediciones en vivo `curl -w` contra prod (2026-10-18); `.github/workflows/fly-deploy.yml`
  (smoke `/health`).
- [memory] aidlc-shared/operation-fly-stack.md; project.md (coste 0 €).

## Assumptions & Open Questions

None.
