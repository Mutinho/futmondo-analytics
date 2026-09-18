# Preguntas de Análisis de Requisitos — Backend Security Hardening

> Scope `security-patch` (Minimal). Cinco correcciones acotadas sobre el backend FastAPI.
> Base de conocimiento del código en `aidlc/spaces/default/codekb/futmondo-analytics/`.
> Responde en el tag `[Answer]:` con la letra elegida (o `X` + texto libre).

## Q1 — Validación de `price` en pujas (FR6): comportamiento ante un valor inválido

Hoy `market.py::place_bid` acepta `price` sin validar; solo el frontend valida (mínimo = valor de mercado, máximo = puja máxima, positivo). Al añadir validación en el backend, ¿qué debe comprobar y qué debe devolver ante un valor inválido, antes de proxyar a Futmondo?

- A. Solo positividad y tipo entero: `price` debe ser un entero > 0; si no, devolver 422 (error de validación) sin llamar a Futmondo.
- B. Positividad + rango con datos ya disponibles en backend: además de > 0, validar contra el máximo de puja del usuario si el backend ya lo conoce sin una llamada extra a Futmondo; si no lo conoce barato, solo positividad.
- C. Replicar toda la validación del frontend (mín. valor de mercado, máx. puja): exige que el backend obtenga esos límites (posible llamada extra a Futmondo).
- D. Solo positividad, devolviendo 400 (bad request) en vez de 422.
- X. Other (please specify)

[Answer]: A

## Q2 — Exposición del endpoint de fotos (FR7): decisión de negocio

El scan confirma que `GET /api/v1/photos/{player_id}` SÍ está protegido por el middleware (no está en `AUTH_EXCLUDED_PATHS`, exige Bearer token). La superficie realmente sin autenticación es la ruta `/static/photos/*` (StaticFiles, fuera del prefijo protegido), a la que el endpoint redirige. ¿Cuál es la intención de negocio para las fotos de jugadores?

- A. Las fotos son públicas a propósito (se muestran en `<img>` sin token): documentar que `/static/photos/*` es público intencionalmente y que `/api/v1/photos/{id}` queda protegido; entregable = documentación + test que congele el comportamiento actual.
- B. Las fotos deben requerir autenticación: proteger también `/static/photos/*` (moverlas tras auth o servirlas por el endpoint autenticado), con test de regresión.
- C. Mantener el endpoint `/api/v1/photos/{id}` protegido pero dejar `/static/photos/*` público, y además documentarlo explícitamente en el código/README (statu quo + doc, sin cambio funcional).
- X. Other (please specify)

[Answer]: A

## Q3 — Aislamiento de `SSL_VERIFY` (FR8): mecanismo

`SSL_VERIFY=0` solo aparece en `docker-compose.yml` (local) y hoy NINGÚN módulo Python lo lee (flag huérfano); no está en `fly.toml`. ¿Cómo aislarlo de forma inequívoca al entorno local?

- A. Eliminar el flag huérfano: si nadie lo consume, borrar `SSL_VERIFY=0` de `docker-compose.yml` y añadir un test/aserción que verifique que ningún cliente HTTP desactiva la verificación TLS en producción.
- B. Cablearlo explícitamente pero con default seguro: hacer que el cliente HTTP lea `SSL_VERIFY` con default `1` (verificación activa), documentar que solo el compose local lo pone a `0`, y añadir test de que producción/Fly.io usa verificación activa.
- C. Ambas: cablear con default seguro (B) y además una comprobación que falle si `SSL_VERIFY=0` llegara a la config de producción.
- D. Solo documentar: dejar el flag como está y documentar que es local; sin cambio de código (más débil).
- X. Other (please specify)

[Answer]: A

## Q4 — Alcance de los tests de regresión y suite existente

La naturaleza del intent es «verificar y, si aplica, corregir con test de regresión». Confirma el alcance de testing (posture del equipo: `pytest`, test-after, sin piso porcentual bloqueante, caminos nuevos y de error cubiertos, suite existente en verde).

- A. Un test dirigido por FR: al menos un test por FR que congele el comportamiento correcto (o el corregido), cubriendo el camino de error donde aplique; la suite existente debe seguir en verde. Para FR9, actualizar deliberadamente los tests de caracterización que hoy congelan el bug.
- B. Como A, pero además reforzar FR18 con casos extra más allá del test existente (`test_db_admin_guard.py`).
- C. Cobertura mínima solo donde hoy no hay ningún test (FR6, FR8), reusando los tests existentes para FR9/FR18 sin tocarlos.
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Resumen de las decisiones:

- FR6 (validar `price` en pujas): validar en `market.py::place_bid` que `price` sea entero > 0; devolver 422 sin llamar a Futmondo si es inválido.
- FR7 (fotos): `/api/v1/photos/{id}` ya está protegido; `/static/photos/*` es público a propósito. Entregable = documentarlo + test que congela el comportamiento actual.
- FR8 (`SSL_VERIFY`): eliminar el flag huérfano de `docker-compose.yml` + test/aserción de que ningún cliente HTTP desactiva la verificación TLS en producción.
- FR9 (`is_refresh_token_valid`): corregir el bug de precedencia naive/aware con test de regresión; actualizar deliberadamente los tests de caracterización que hoy congelan el bug.
- FR18 (`/database/reset`|`/populate`): confirmar la guarda `ENABLE_DB_ADMIN` (404 por defecto) y añadir/consolidar test que la verifique.
- Testing: un test dirigido por FR cubriendo camino de error donde aplique; suite existente en verde; sin piso porcentual bloqueante.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
