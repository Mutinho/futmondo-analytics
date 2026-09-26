# Reliability Design — Intent 4 (gate CI/CD hardening)

> Etapa de diseño: patrones y decisiones, no implementación.

## Alcance

La fiabilidad relevante es la **del propio gate de CI/CD como red de seguridad**:
debe ser **reproducible** (mismo veredicto ante el mismo commit), **determinista**
(sin flapping) y con **rollback quirúrgico**. La disponibilidad de la aplicación
en runtime (SLA/SLO de la app, tolerancia a fallos, recovery de datos) **no
cambia** con este intent.

## Diseño de fiabilidad del gate

### R1 — Gate reproducible (NFR5.1)

El veredicto no debe depender de qué resuelva el gestor de paquetes ese día. Dos
palancas de diseño:

- **Superficie estable**: `pip-audit` audita el **entorno instalado/resuelto**
  (no rangos de `requirements.txt`). `npm audit` corre sobre el árbol que
  `npm ci` dejó instalado (lockfile).
- **Tooling pinneado**: `ruff`, `pip-audit`, `vitest` y `gitleaks` a versión
  exacta (ver security-design C5). Un tooling flotante puede introducir reglas
  nuevas y cambiar el veredicto entre ejecuciones.

Criterio: dos ejecuciones sobre el mismo commit dan el mismo resultado.

### R2 — Sin flapping en el piso de cobertura (NFR5.2)

- El piso `--cov-fail-under` se fija al **valor medido exacto SIN margen** sobre
  la suite ya estabilizada (medición en ci-pipeline, Q5=A).
- Un rojo intermitente por no-determinismo se resuelve **arreglando el test
  no-determinista**, NUNCA bajando el piso ni añadiendo margen de holgura.
- El piso es **line-only** (no se añade `--cov-branch`).

### R3 — Rollback quirúrgico (NFR2.1)

- Cada endurecimiento (piso de cobertura, promoción advisory→bloqueante de un
  audit/lint, unificación/pin de una versión) va en su **propio commit
  `chore(ci)` aislado** con el trinquete fijado.
- Cada check bloqueante se diseña como **paso identificable y aislado**
  (decisión Q3=A), de modo que revertir uno no arrastre los demás y el fallo sea
  localizable sin leer todo el log.
- Mecanismo de rollback de release: redeploy de la release anterior con Fly.io
  (`fly releases rollback`), runbook en `docs/ROLLBACK.md` (sin cambios).

### R4 — Cadena de release intacta (NFR-REL.1)

- El endurecimiento refuerza el **CONTENIDO** del job `verify`, **sin reordenar**
  la cadena `needs:` (`verify → deploy-backend → deploy-frontend → smoke-test`).
- El smoke test `/health` (5 reintentos, HTTP 200) sigue siendo la verificación
  de release. Sin staging separado.

### R5 — El gate no relaja garantías (NFR-REL.2)

- Ningún endurecimiento puede bajar un umbral/piso existente ni dejar
  `continue-on-error` permanente en un check promovido.
- El **ratchet (backend y frontend) sólo sube**. Un finding sin fix va a la
  allowlist con caducidad (security-design C4), nunca a un silenciador
  permanente; una entrada caducada vuelve a bloquear.

## Patrones de resiliencia aplicables (adaptados, coste 0 €)

Los patrones clásicos de resiliencia de runtime (circuit breaker, bulkhead,
retry con backoff) **no aplican** al código de la app en este intent. El único
patrón de reintento presente y preservado es el **smoke test** del release:
5 reintentos contra `/health` esperando HTTP 200 — reintento acotado que ya
existe y no se modifica.

## Runtime de la app — N/A (justificado)

SLA/SLO de disponibilidad de la app, tolerancia a fallos del servicio,
backup/recovery de Neon y degradación elegante: **N/A**. Son las garantías de la
línea base en producción y no cambian.

## Trazabilidad

- NFR5.1 → R1; NFR5.2 → R2; NFR2.1 → R3; NFR-REL.1 → R4; NFR-REL.2 → R5.

## Sources

- `../nfr-requirements/reliability-requirements.md` (NFR5.1, NFR5.2, NFR2.1, NFR-REL.1, NFR-REL.2).
- `aidlc/spaces/default/memory/team.md` §Deployment / §Testing Posture (Q6, ratchet).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (rollback, smoke test).

## Assumptions & Open Questions

- El valor numérico del piso backend (NFR5.2) se mide en ci-pipeline; la política (valor exacto, sin margen, sólo trinquete) ya está afirmada.
