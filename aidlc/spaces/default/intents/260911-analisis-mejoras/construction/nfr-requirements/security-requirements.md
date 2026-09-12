# Requisitos de Seguridad — Plan de Mejoras de futmondo-analytics


> Requisitos no funcionales de seguridad, medibles, derivados de los hallazgos
> del análisis y del NFR2 de `requirements.md`. Adaptados a coste 0 € (solo tiers
> gratuitos) y a un mantenedor único. No se implementan aquí. Trazabilidad de NFR2
> → NFR2.1–NFR2.9 en `traceability.json`. [requirements] [technology-stack] [memory:M1]

## Autenticación y sesión



- **NFR2.1** — El sistema NO almacena la contraseña Futmondo en claro en ningún
  almacén (memoria, disco o BD). Verificación: inspección de `SessionStore`; la
  contraseña no aparece en volcados de estado. Origen: FR5. [requirements]
- **NFR2.2** — El JWT mantiene la postura actual endurecida: fail-fast del secreto
  en arranque, access token 60 min en memoria, refresh 30 días en cookie HttpOnly.
  Verificación: arranque falla sin `JWT_SECRET`; el refresh no es accesible desde JS.
- **NFR2.3** — La expiración del refresh token se evalúa correctamente (sin
  ambigüedad naive/aware). Verificación: test dedicado que compruebe expiración
  en el pasado y en el futuro. Origen: FR9 (a verificar). [requirements]

## Autorización y superficie de API

- **NFR2.4** — Todos los endpoints `/api/v1/*` requieren Bearer token salvo la
  lista explícita `AUTH_EXCLUDED_PATHS`. Verificación: una petición sin token a
  un endpoint protegido devuelve 401.
- **NFR2.5** — Los endpoints destructivos (`/database/reset`, `/database/populate`)
  devuelven 404 en producción salvo con `ENABLE_DB_ADMIN` activado. Verificación:
  test de guarda que confirme 404 con la variable desactivada. Origen: FR18 (a verificar). [requirements]
- **NFR2.6** — El endpoint `GET /api/v1/photos/{player_id}` tiene una política de
  auth explícita y documentada (protegido, o excepción intencional en
  `AUTH_EXCLUDED_PATHS`). Verificación: confirmar accesibilidad y documentarla.
  Origen: FR7 (a verificar). [requirements]

## Validación de entrada

- **NFR2.7** — Toda entrada de usuario que llega al backend se valida en el
  backend, no solo en el cliente. En particular, `POST /api/v1/market/bid` rechaza
  `price` no positivo o fuera de rango antes de proxyar a Futmondo. Verificación:
  petición directa con `price` inválido devuelve error de validación. Origen: FR6. [requirements]

## Transporte y secretos

- **NFR2.8** — La verificación TLS está activa en producción; `SSL_VERIFY=0` queda
  confinado al entorno local de forma inequívoca. Verificación: confirmar que la
  variable no se propaga a la config de producción. Origen: FR8 (a verificar). [requirements]
- **NFR2.9** — No hay secretos en el repositorio; gitleaks se mantiene bloqueante
  en CI. Verificación: el workflow `ci.yml` falla si detecta un secreto.

## Consideraciones de amenazas (STRIDE, resumen)

- **Spoofing/Elevation**: mitigado por JWT + middleware de auth (NFR2.2, NFR2.4).
- **Tampering**: validación de entrada en backend (NFR2.7).
- **Information disclosure**: credenciales fuera de memoria en claro (NFR2.1),
  TLS en producción (NFR2.8), sin secretos en repo (NFR2.9).
- **Denial of service**: fuera de alcance de objetivos numéricos dada la escala
  pequeña (ver `reliability-requirements.md`); las integraciones externas frágiles
  se tratan en fiabilidad.

## Cumplimiento

- No hay obligaciones regulatorias formales declaradas (proyecto personal, grupo
  reducido). Se aplica higiene de datos básica: no almacenar credenciales en claro
  (NFR2.1) y no registrar datos sensibles en logs (ver `observability-requirements.md`).
  [assumption]

## Assumptions & Open Questions

- Se asume que no hay requisitos regulatorios (RGPD formal, etc.) por el carácter
  personal del proyecto; si la base de usuarios creciera fuera del círculo, habría
  que revisar el tratamiento de datos personales. [assumption]
