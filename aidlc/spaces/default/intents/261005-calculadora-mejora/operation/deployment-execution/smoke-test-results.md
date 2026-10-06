# Smoke Test Results — calculadora-mejora

## Mecanismo

El smoke test del release es el job `smoke-test` de `fly-deploy.yml`: tras
`deploy-frontend`, hace hasta **5 reintentos** contra `/health` esperando
**HTTP 200**. Un fallo aborta el release (y queda la release anterior sana para
rollback).

## Resultado

- **Smoke test automatizado (`/health`)**: se ejecuta en el pipeline al mergear;
  **pendiente** hasta el merge a `main`.
- **Verificación funcional manual recomendada tras el deploy** (frontend-only,
  no automatizable en el smoke de infraestructura):
  1. Abrir `/calculator`; confirmar el toggle "Incorporar jugadores en venta".
  2. Toggle ON: bloque "En venta" visible, jugadores en venta excluidos de la lista, saldo futuro incluye su total.
  3. Toggle OFF: bloque "En venta" oculto, esos jugadores en la lista (deseleccionados), saldo futuro sin su total; pujas activas siguen restando.
  4. Recargar: el estado del toggle se conserva (`localStorage`).

## Cobertura equivalente ya verificada

- Los puntos 1–4 están cubiertos por los 13 specs del componente (verde en CI),
  que aseveran el efecto sin red/backend.

## Sources

- `fly-deploy.yml` (job `smoke-test`); `construction/build-and-test/test-results.md`.

## Assumptions & Open Questions

None.
