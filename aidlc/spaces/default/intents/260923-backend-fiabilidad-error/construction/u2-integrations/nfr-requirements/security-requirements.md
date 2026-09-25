# Security Requirements — u2-integrations (Integraciones)

Alcance de seguridad acotado (Q4): la intervención de U2 no cambia
autenticación/autorización ni expone API pública nueva. La superficie de
seguridad relevante de esta unidad es (1) el manejo de credenciales del usuario
hacia Futmondo y lo que sale en logs/excepciones, y (2) la integridad de los
datos ante fallo. El resto de controles se hereda del sistema y se documenta
como "sin cambio en este intent".

Consume: `functional-spec.md`, `rules.md`, `requirements.md`, `contract-summary.md`,
`technology-stack.md`. Perspectivas inline: DevSecOps (STRIDE), Compliance, QA.

## Requisitos de seguridad (derivados)

| ID | Requisito | Categoría STRIDE | Fuente | Verificación |
|----|-----------|------------------|--------|--------------|
| NFR3.1 | Ninguna excepción de integración incluye password ni token del usuario en su mensaje, `__str__`/`repr` ni `exc_info`. | Information Disclosure | NFR3, práctica afirmada | Spec que construye la excepción y asvera que el texto/`repr` no contiene el secreto |
| NFR3.2 | El log estructurado de fallo de integración lleva sólo contexto no sensible (`sync_step`, `failure_mode`, `status`, `endpoint`, `task_id`, `reason`); nunca credenciales. | Information Disclosure | NFR1, NFR3 | Spec que asvera los campos emitidos y la ausencia de credenciales; `gitleaks` sobre tests |
| NFR3.3 | Las excepciones de integración internas van en INGLÉS (diagnóstico de desarrollador); el texto de cara al usuario (`HTTPException.detail`) en CASTELLANO — sin filtrar detalle interno sensible al borde HTTP. | Information Disclosure | práctica afirmada (Code Style) | Revisión + specs de borde |
| NFR2.1 | Ante fallo fatal en un punto de escritura (p. ej. `team_prizes`), la tabla/caché queda todo-o-nada; no se dejan datos parciales que un consumidor lea como válidos. | Tampering / Integridad | NFR2 (functional-design BR5.1/BR5.2) | Spec que fuerza el fallo y asvera el estado consistente |
| NFR3.4 | Los secretos (credenciales Futmondo, `JWT_SECRET`, `DATABASE_URL`) se gestionan vía `fly secrets` / GitHub Actions secrets; nunca literales en código, workflow ni tests (los tests usan dobles/fakes). | Information Disclosure / Secrets | práctica afirmada, Deployment | `gitleaks` bloqueante en CI (PR) y `verify` (push) |

## Modelo de amenazas (STRIDE acotado a U2)

| Amenaza | ¿Relevante en U2? | Tratamiento |
|---|---|---|
| **S**poofing | Sin cambio | Auth JWT (access en memoria, refresh HttpOnly cookie) heredada; U2 no la toca. |
| **T**ampering | **Sí** | No-corrupción de datos ante fallo (NFR2.1): reemplazo transaccional atómico en `team_prizes`. |
| **R**epudiation | Sin cambio | Fuera del alcance (no hay acción de usuario nueva que auditar en U2). |
| **I**nformation Disclosure | **Sí (foco)** | NFR3.1–NFR3.4: nunca credenciales en excepción/`repr`/`exc_info`/log; secretos gestionados. |
| **D**enial of Service | Parcial | Timeout acotado por petición (ver performance-requirements NFR-perf) evita que un proveedor colgado bloquee el sync; rate-limiting preventivo de Sofascore se mantiene. Sin cambios de infra. |
| **E**levation of Privilege | Sin cambio | U2 no cambia authz ni añade endpoints; heredado. |

## Controles heredados (sin cambio en este intent)

- Autenticación JWT (access token en memoria 1h, refresh token HttpOnly cookie 30d) y autorización de endpoints `/api/v1/*` — **sin cambio**.
- Cifrado en tránsito a Neon (TLS) y hacia los proveedores externos (HTTPS) — **sin cambio**.
- Rate-limiting de API y del cliente Sofascore (throttle ~750 ms) — **sin cambio**; U2 no lo modifica.
- `JWT_SECRET` no-default exigido en arranque (NFR1.1 de intents previos, `test_jwt_startup.py`) — **sin cambio**, sigue vigente.

## Cumplimiento (Compliance)

No hay marco regulatorio nuevo aplicable (proyecto personal, sin PII de terceros
regulada más allá de las propias credenciales del usuario, que precisamente se
protegen por NFR3). No aplica PCI/HIPAA/SOC2/GDPR formal en el alcance de U2; la
protección de credenciales (NFR3) es la obligación de facto y queda cubierta.

## Assumptions & Open Questions

None.
