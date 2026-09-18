# Requisitos de Seguridad — Backend Security Hardening

> Scope `security-patch`, depth Minimal. Este es el artefacto central del intent.
> **Esquema de IDs**: los requisitos detallados de seguridad heredan del NFR de
> seguridad de inception **NFR1** (el único NFR de inception cuyo tema es seguridad)
> y añaden sub-número (`NFR1.1`, `NFR1.2`, …), conforme a la regla de la etapa
> ("cada requisito detallado hereda su ID de inception y añade un sub-número").
> Los NFR de inception NFR2 (compatibilidad de stack), NFR3 (coste 0 €), NFR4
> (gate CI) y NFR5 (testabilidad) se detallan en los artefactos hermanos
> (`scalability-`, `tech-stack-`, `reliability-`, `observability-requirements.md`)
> con sus prefijos propios (`NFR-SCAL`, `NFR-TECH`, `NFR-REL`, `NFR-OBS`), por lo
> que este documento no reutiliza `NFR2.x`–`NFR6.x` y no colisiona con ellos.

## Modelo de Autenticación y Autorización (no regresión)

- **NFR1.1**: Toda ruta `/api/v1/*` y `/auth/*` (salvo `AUTH_EXCLUDED_PATHS`) sigue exigiendo `Authorization: Bearer <access>` verificado con `expected_type="access"` vía `AuthMiddleware`. Ninguna corrección debe abrir una ruta protegida ni añadir una exclusión no justificada. Traza: FR7, NFR1. `[memory:api-documentation.md]`
- **NFR1.2**: El arranque del servicio web sigue exigiendo un `JWT_SECRET` no-default en producción (guard `resolve_jwt_secret`, endurecido en `test_jwt_startup.py`); ninguna corrección lo debilita. Traza: NFR1, regla `## Forbidden` del proyecto. `[memory:project.md]`
- **NFR1.3** (FR9): La validación del refresh token (`is_refresh_token_valid`) debe aceptar tokens activos y rechazar los expirados o revocados de forma correcta e inequívoca ante `expires_at` naive **o** aware. Un token activo con `expires_at` aware nunca debe rechazarse por error. Traza: FR9, NFR1. `[Q4:requirements-analysis]`

## Validación de Entrada (defensa en el backend)

- **NFR1.4** (FR6): El endpoint de pujas (`market.py::place_bid`) debe validar `price` en el backend antes de proxyar a Futmondo: entero estrictamente positivo (`price > 0`). Entrada inválida → HTTP 422, sin efecto lateral (sin llamada a Futmondo). La validación de frontend no cuenta como control de seguridad (evadible llamando la API directamente). Traza: FR6, NFR1. `[memory:phases/construction.md]`
- **NFR1.5** (FR6): La validación se aplica en el boundary del sistema (el router/endpoint) como manda el guardrail de fase de Construcción ("Validate and sanitize all inputs at system boundaries"), sin ampliar el patrón SQL-en-router ni los god-files. Traza: FR6, NFR1. `[memory:team.md]`

## Protección de Datos y Superficie Estática

- **NFR1.6** (FR7): Se documenta explícitamente que `/api/v1/photos/{player_id}` está protegido por el middleware y que `/static/photos/*` es una superficie **pública intencionada** (imágenes de jugadores, no datos sensibles ni específicos de usuario). Un test congela ambos comportamientos. No se expone ningún dato sensible por la vía pública. Traza: FR7, NFR1. `[Q2:requirements-analysis]`
- **NFR1.7** (FR5/FR9): Ninguna corrección reintroduce credenciales (password Futmondo) en claro, ni en memoria ni en base de datos. Traza: NFR1, regla `## Forbidden` del proyecto. `[memory:project.md]`

## Seguridad de Transporte

- **NFR1.8** (FR8): Ningún cliente HTTP del backend (`requests`, `curl_cffi`) desactiva la verificación TLS (`verify=False` o equivalente) en la ruta de producción. Se elimina el flag huérfano `SSL_VERIFY=0` de `docker-compose.yml` y una aserción/test estático verifica que no reaparezca deshabilitación de TLS en la configuración productiva. Traza: FR8, NFR1. `[Q3:requirements-analysis]`

## Endpoints de Administración

- **NFR1.9** (FR18): Los endpoints `POST /api/v1/database/reset` y `/populate` devuelven 404 salvo con `ENABLE_DB_ADMIN` afirmativo (`_require_db_admin`), cerrando la superficie de administración por defecto en producción. Cubierto por test (404 por defecto, 404 con valor no afirmativo, acceso con flag activo). Traza: FR18, NFR1. `[memory:code-quality-assessment.md]`

## Consideraciones de Amenaza (STRIDE, acotado al intent)

- **Tampering / Elevation** (FR6): un cliente que evade el frontend podía enviar `price` arbitrario (negativo, cero, no numérico) al proxy de pujas → mitigado por NFR1.4/NFR1.5.
- **Information disclosure** (FR7): confirmar que fotos no filtran datos sensibles y que la única superficie pública es la estática intencionada → NFR1.6.
- **Spoofing / MITM** (FR8): desactivar TLS habilitaría interceptación; se elimina el vector huérfano → NFR1.8.
- **Elevation of privilege** (FR18): endpoints destructivos de administración cerrados por defecto → NFR1.9.
- **Denial of service / repudiation**: fuera del alcance de este intent (sin cambios de rate-limiting ni de auditoría en este patch).

## Cumplimiento y Coste (referencia cruzada)

- **Coste 0 €**: ninguna corrección de seguridad introduce dependencias o servicios de pago; el detalle vive en `tech-stack-decisions.md` (`NFR-TECH.1`) y `scalability-requirements.md` (`NFR-SCAL.1`), que detallan el NFR de inception NFR3. Traza: NFR3, regla `## Mandated` del proyecto. `[memory:project.md]`
- **Cumplimiento**: no hay marcos regulatorios adicionales aplicables a este patch (fantasy football, sin PII sensible más allá de credenciales delegadas ya protegidas). Perspectiva de cumplimiento: sin nuevos controles obligatorios.

## Sources

- `[Q<n>:requirements-analysis]` Respuestas confirmadas en `requirements-analysis-questions.md` (etapa de Análisis de Requisitos), heredadas como contexto. En **esta** etapa (NFR Requirements) solo se preguntó Q1 (método = A: derivar los NFR de los requisitos aprobados y la base de código, sin abrir preguntas nuevas de targets); ver `nfr-requirements-questions.md`.
- `[memory:...]` Base de conocimiento del código (`aidlc/spaces/default/codekb/futmondo-analytics/`) y reglas (`aidlc/spaces/default/memory/`).
- Requisitos de inception: `requirements.md` (FR6–FR18, NFR1–NFR5).

## Assumptions & Open Questions

None. Los supuestos de negocio (fotos públicas intencionadas; ningún flujo local necesita desactivar TLS) fueron confirmados en Análisis de Requisitos y se heredan como base de NFR1.6 y NFR1.8.
