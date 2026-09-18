# Requisitos — Backend Security Hardening (futmondo-analytics)

## Análisis de Intención

El objetivo es **reducir la superficie de abuso del backend FastAPI** agrupando cinco correcciones de seguridad de esfuerzo pequeño provenientes del plan del intent `260911-analisis-mejoras`. La naturaleza del trabajo es «verificar y, si aplica, corregir con test de regresión»: cuando un comportamiento ya es correcto en producción, el entregable es un test que lo congela; cuando hay un defecto, el entregable es la corrección más su test.

No se persiguen features nuevas ni reescrituras: se endurecen puntos concretos (validación de entrada de pujas, exposición de un endpoint, un flag de configuración huérfano, un bug de validación de refresh token y una guarda de administración) manteniendo el stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io) y el mandato de coste 0 € (tiers gratuitos).

## Requisitos Funcionales

### FR6 — Validación de `price` en el backend de pujas

- **FR6.1**: `market.py::place_bid` debe validar que el parámetro `price` sea un entero estrictamente positivo (`price > 0`) **antes** de proxyar la puja a Futmondo. `[desc]`
- **FR6.2**: Si `price` es inválido (no entero, cero o negativo), el backend debe rechazar la petición con **HTTP 422** (error de validación) y **no** realizar la llamada a Futmondo. `[Q1]`
- **FR6.3**: La validación reside en el backend y no depende del frontend; el hallazgo es que hoy solo el frontend valida y la API es evadible llamándola directamente. `[scope]` `[memory:code-quality-assessment.md]`

Criterio de aceptación (Given/When/Then):
```
Given un usuario autenticado con Bearer token válido
When envía POST /api/v1/market/bid con price = 0 (o negativo, o no entero)
Then el backend responde 422 y no invoca la API de Futmondo

Given un usuario autenticado con Bearer token válido
When envía POST /api/v1/market/bid con price entero positivo
Then el backend proxya la puja a Futmondo como hoy
```

### FR7 — Exposición del endpoint de fotos de jugadores

- **FR7.1**: Confirmar y **documentar** que `GET /api/v1/photos/{player_id}` está protegido por `AuthMiddleware` (no figura en `AUTH_EXCLUDED_PATHS`; exige Bearer token). `[desc]` `[memory:api-documentation.md]`
- **FR7.2**: Documentar que la ruta `/static/photos/*` (StaticFiles) es **pública a propósito** por quedar fuera del prefijo protegido, y que las fotos de jugadores no son datos sensibles ni específicos de usuario. `[Q2]`
- **FR7.3**: Entregable = documentación (código/README) + test que congela el comportamiento actual (endpoint protegido; estáticas públicas). Sin cambio funcional. `[Q2]`

Criterio de aceptación:
```
Given una petición sin Bearer token
When accede a GET /api/v1/photos/{player_id}
Then el backend responde 401/403 (protegido por middleware)

Given una petición sin Bearer token
When accede a /static/photos/<archivo>
Then el recurso se sirve (público a propósito), y este comportamiento queda documentado
```

### FR8 — Aislamiento del flag `SSL_VERIFY`

- **FR8.1**: Eliminar el flag huérfano `SSL_VERIFY=0` de `docker-compose.yml`, dado que ningún módulo Python lo consume hoy y no existe en `fly.toml`. `[Q3]` `[memory:code-quality-assessment.md]`
- **FR8.2**: Añadir un test/aserción que verifique que ningún cliente HTTP del backend desactiva la verificación TLS (`verify=False` o equivalente) en la ruta de producción. `[Q3]`

Criterio de aceptación:
```
Given la configuración del repositorio tras el cambio
When se inspeccionan docker-compose.yml y la configuración de los clientes HTTP
Then SSL_VERIFY=0 no está presente y ningún cliente HTTP desactiva la verificación TLS

Given la suite de tests
When se ejecuta el test de verificación TLS
Then falla si algún cliente HTTP productivo deshabilita la verificación TLS
```

### FR9 — Corrección del bug de `is_refresh_token_valid`

- **FR9.1**: Corregir en `backend/app/auth/token_store.py::is_refresh_token_valid` el ternario de precedencia ambigua que mezcla `datetime.now(timezone.utc)` con un `expires_at` naive/aware, de modo que un refresh token **activo** con `expires_at` aware (caso real PostgreSQL) se valide correctamente y no se rechace por error. `[desc]` `[memory:code-quality-assessment.md]`
- **FR9.2**: Añadir un test de regresión que congele el comportamiento **correcto** (token aware futuro → válido; token expirado → inválido; token revocado → inválido). `[Q4]`
- **FR9.3**: Actualizar deliberadamente y de forma trazable los tests de caracterización existentes (`test_auth_characterization.py`) que hoy congelan el comportamiento **defectuoso**, ya que el comportamiento esperado cambia a propósito. `[Q4]`

Criterio de aceptación:
```
Given un refresh token no revocado con expires_at aware en el futuro
When se llama is_refresh_token_valid(token_hash)
Then devuelve True (token válido)

Given un refresh token con expires_at en el pasado, o revocado
When se llama is_refresh_token_valid(token_hash)
Then devuelve False
```

### FR18 — Guarda de los endpoints de administración de base de datos

- **FR18.1**: Confirmar que `POST /api/v1/database/reset` y `POST /api/v1/database/populate` devuelven **404** salvo cuando `ENABLE_DB_ADMIN` está activo (`∈ {1,true,yes,on}`), mediante `_require_db_admin()`. `[desc]` `[memory:api-documentation.md]`
- **FR18.2**: Asegurar cobertura de test que verifique la guarda: 404 por defecto, 404 con valor no afirmativo, y acceso permitido con `ENABLE_DB_ADMIN` activo. El test `test_db_admin_guard.py` ya existe; consolidar si el diseño lo requiere. `[Q4]` `[memory:code-quality-assessment.md]`

Criterio de aceptación:
```
Given ENABLE_DB_ADMIN no está activo (default de producción)
When se llama POST /api/v1/database/reset o /populate
Then el backend responde 404

Given ENABLE_DB_ADMIN activo
When se llama POST /api/v1/database/reset o /populate
Then la operación de administración se ejecuta
```

## Requisitos No Funcionales

- **NFR1 — Seguridad (no regresión)**: Ninguna corrección debe reintroducir credenciales en claro ni un `JWT_SECRET` por defecto en producción, ni debilitar controles de auth existentes (reglas `## Forbidden` del proyecto). `[memory:project.md]`
- **NFR2 — Compatibilidad de stack**: Las correcciones mantienen el stack actual (Angular 22 + FastAPI/Python 3.12 + Neon PostgreSQL + Fly.io) sin reescrituras grandes ni ampliar los god-files ni el patrón SQL-en-router. `[scope]` `[memory:code-structure.md]`
- **NFR3 — Coste 0 €**: Ninguna corrección introduce dependencias o servicios con gasto recurrente; todo se mantiene en tiers gratuitos. `[memory:project.md]`
- **NFR4 — Gate de CI verde**: Todos los cambios pasan el gate bloqueante de CI (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; la suite existente permanece en verde. `[memory:project.md]`
- **NFR5 — Testabilidad (test-after, dirigido por FR)**: Al menos un test verificable por FR que congele el comportamiento correcto o el corregido, cubriendo el camino de error donde aplique; sin piso porcentual bloqueante adicional. `[Q4]` `[memory:team.md]`

## Restricciones

- Mantener el stack actual sin reescrituras grandes (constraint del intent). `[scope]`
- Coste 0 € (Neon free, Fly.io free allowance, GitHub Actions free). `[memory:project.md]`
- Idioma en el código: identificadores, docstrings y comentarios en inglés; texto de usuario (`HTTPException.detail`) en castellano. `[memory:team.md]`
- Backend testeado con `pytest` desde `backend/` (`pytest.ini`: `testpaths=tests`, `pythonpath=.`); usar los fakes de `conftest.py` en vez de servicios reales. `[memory:team.md]`
- No ampliar el SQL-en-router ni los god-files (`data_manager_v2.py`, `data_sync_service.py`); si hace falta acceso a datos nuevo, tras una capa estrecha. `[memory:team.md]`

## Supuestos

- **[assumption]** Las fotos de jugadores no contienen datos personales sensibles y su exposición pública vía `/static/photos/*` es aceptable para el negocio (base de la decisión FR7). Propietario: producto/usuario; validado en Q2.
- **[assumption]** Ningún flujo local legítimo necesita desactivar la verificación TLS, por lo que eliminar `SSL_VERIFY` (FR8) no rompe el desarrollo local. Validado en Q3; si apareciera un servicio local con certificado autofirmado, se reconsideraría un cableado con default seguro.
- **[assumption]** La guarda `ENABLE_DB_ADMIN` (FR18) ya es correcta en producción; el trabajo es confirmar/consolidar su test, no rediseñarla.

## Fuera de Alcance

- Refactorizar la persistencia de auth hacia una capa repositorio unificada (más allá de la corrección puntual de FR9).
- Reducir o dividir los god-files de `services/`.
- Endurecer el job `verify` de `fly-deploy.yml` para replicar el gate de PR (queda para diseño de pipeline).
- Cualquier cambio en el frontend salvo lo estrictamente necesario (la validación de FR6 es backend).

## Preguntas Abiertas

- Ninguna bloqueante para el diseño. Nota para etapas posteriores: si FR18 requiere consolidar el test existente en vez de añadir uno nuevo, decidirlo en generación de código según el estado real de `test_db_admin_guard.py`.

## Sources

- `[desc]` Initial description: descripción autoritativa del intent (`project-description.json`, verbatim vía `aidlc engine workspace project-description`).
- `[scope]` Workflow-selected scope: `security-patch` (depth Minimal, test strategy Minimal).
- `[Q1]`–`[Q4]` Respuestas confirmadas en `requirements-analysis-questions.md` (modo guiado).
- `[memory:...]` Base de conocimiento del código en `aidlc/spaces/default/codekb/futmondo-analytics/` (`business-overview.md`, `architecture.md`, `code-structure.md`, `api-documentation.md`, `code-quality-assessment.md`) y reglas de `aidlc/spaces/default/memory/` (`project.md`, `team.md`).

## Assumptions & Open Questions

Ver las secciones `## Supuestos` y `## Preguntas Abiertas` arriba. Los supuestos etiquetados `[assumption]` permanecen como supuestos hasta que una etapa posterior los confirme; no se promueven silenciosamente a requisitos confirmados.
