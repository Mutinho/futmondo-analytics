# Security Design — u2-integrations (Integraciones)

Diseño de los controles de seguridad de U2, derivado de `security-requirements.md`
(NFR3.1–3.4). Alcance acotado: protección de credenciales (no disclosure) e
integridad de datos; el resto de controles (auth/authz, TLS, rate-limiting) se
hereda sin cambio. Adaptado a Fly.io + Neon, coste 0 € — sin KMS/IAM/Secrets
Manager de AWS (NO-APLICA; se usan `fly secrets`/GitHub secrets).

Consume: `security-requirements.md`, `functional-spec.md`, `tech-stack-decisions.md`,
`contract-summary.md`. Perspectivas inline: arquitecto + plataforma (Fly.io).

## Diseño por requisito

### NFR3.1 / NFR3.2 — No filtrar credenciales en excepciones ni logs

- **Diseño**: las clases de `integration_errors` construyen su mensaje SÓLO a
  partir de contexto no sensible (`failure_mode`, `status`, `endpoint`). El
  constructor NUNCA recibe ni almacena password/token; si un llamador tiene la
  credencial en una variable local, no se pasa a la excepción.
- **Logging**: un helper de logging estructurado recibe un dict de campos
  permitidos (`sync_step`, `failure_mode`, `status`, `endpoint`, `task_id`,
  `reason`) y emite `clave=valor`. No acepta un objeto de request/credencial
  completo; se pasan campos explícitos, evitando volcados accidentales.
- **`exc_info`**: al loguear con `exc_info`, la traza no contiene la credencial
  porque ésta no está en el estado de la excepción (ver arriba).

```text
# pseudocódigo (≤15 líneas) — construcción segura de excepción y log
raise IntegrationTimeoutError(failure_mode="timeout", endpoint=ep, status=None)
log.warning("integration failure",
            sync_step=step, failure_mode="timeout", endpoint=ep, task_id=tid)
# ep es una ruta no sensible; nunca se pasa la URL con token ni el password
```

### NFR3.3 — Idioma y no filtrado al borde HTTP

- Mensajes de excepción internos en INGLÉS (diagnóstico). En el borde HTTP, la
  `HTTPException.detail` de cara al usuario va en CASTELLANO y es **genérica**
  (no expone el detalle interno ni el `repr` de la excepción de integración).

### NFR2.1 — Integridad (Tampering) del punto de escritura

- Ver `reliability-design.md`: reemplazo transaccional atómico de `team_prizes`;
  un fallo revierte todo (todo-o-nada). Aquí se referencia como control de
  integridad de datos (STRIDE Tampering).

### NFR3.4 — Gestión de secretos

- **Diseño**: los secretos (credenciales Futmondo del usuario en sesión,
  `JWT_SECRET`, `DATABASE_URL`) se leen de variables de entorno pobladas por
  `fly secrets` (runtime) y GitHub Actions secrets (CI). No hay secretos en
  código, workflow ni tests (fakes/dobles). `gitleaks` bloquea en CI.

## Defensa en profundidad (adaptada)

| Capa | Control | Estado |
|---|---|---|
| Borde HTTP | Auth JWT + HTTPException genérica | Heredado (sin cambio) |
| Cliente de integración | Excepción tipada sin credencial; timeout acotado | **Nuevo (U2)** |
| Logging | Campos permitidos, sin credenciales; `gitleaks` | **Nuevo/endurecido (U2)** |
| Persistencia | Reemplazo transaccional atómico (no-corrupción) | **Endurecido (U2)** |
| Secretos | `fly secrets` / GitHub secrets | Heredado (sin cambio) |

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- AWS KMS / Secrets Manager / IAM least-privilege → NO-APLICA (Fly.io gestiona
  red/routing; secretos vía `fly secrets`). Documentado, no inventado.
- WAF / Shield / GuardDuty → NO-APLICA (de pago); sin equivalente necesario en
  el alcance de U2.

## Assumptions & Open Questions

None.
