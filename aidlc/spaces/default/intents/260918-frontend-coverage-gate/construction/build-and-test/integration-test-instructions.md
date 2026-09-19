# Integration Test Instructions — frontend-coverage-gate

Estrategia **standard**: pruebas de los límites clave e interacción entre piezas. Este intent tiene **una sola unidad** (`frontend-coverage-gate`, kind `packaging`) y **no introduce nuevos límites de integración entre servicios**: es una intervención de tooling/config + specs. Por tanto no hay integración cross-unit que ejercitar.

## Límites cubiertos por los specs sembrados (unit-level con dobles de integración)

Los 12 specs cubren los límites de integración HTTP del frontend con dobles deterministas (sin red), que es la superficie de integración relevante de esta unidad:

- **Servicios `core/services/*` ↔ HTTP** (`auth`, `budget`, `roster`, `favorites`, `championship`, `evolution`, `stats`, `sync`, `analytics`, `assistant`): `provideHttpClient` + `provideHttpClientTesting`; se verifica URL, método, params, payload y headers con `HttpTestingController.expectOne(...).flush(...)` y `httpMock.verify()`.
- **Interceptor `auth.interceptor` ↔ pipeline HTTP**: inyección de `Authorization: Bearer`, cola de refresh ante 401, `withCredentials` para `/auth/*`.
- **Guard `auth.guard` ↔ router/injection context**: `CanActivateFn` invocado dentro de `TestBed.runInInjectionContext(...)`.
- **`assistant.service` ↔ streaming SSE**: `fetch` + `ReadableStream` mockeados de forma determinista (elimina el no-determinismo P2).
- **Componente `bid-dialog` ↔ Material dialog + signals + HTTP**: standalone con `provideHttpClientTesting` y `MatDialog`.

## Integración de sistema (real, fuera de esta suite)

La integración real frontend↔backend↔Neon se ejercita en el pipeline de despliegue existente (smoke test contra `/health` y `/` tras el deploy en Fly.io), inalterado por este intent. No se añade E2E nuevo (fuera de alcance; coste 0 €).

## Cómo ejecutar

El mismo comando de unidad ejerce toda la superficie de integración simulada:

```bash
# desde angular-app/ (o en contenedor node:22.22.3):
npm ci
npx ng test --watch=false
```

## Objetivo de cobertura

Cobertura por métrica sobre `src/app/**/*.ts` (denominador estable), umbral en el target `test` de `angular.json`; trinquete solo-arriba.
