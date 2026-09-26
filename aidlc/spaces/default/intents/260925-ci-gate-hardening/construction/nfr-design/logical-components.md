# Logical Components — Intent 4 (gate CI/CD hardening)

> Etapa de diseño. Puente hacia Infrastructure Design: vista a nivel de
> componente de dónde aplican los patrones NFR. Este intent es config-only de
> CI/CD; los "componentes lógicos" son los del **propio gate** (decisión Q4=A),
> no infraestructura de aplicación nueva.

## Enfoque

Se modela el gate de CI/CD como un conjunto de **componentes lógicos = dominios
de fallo**, cada uno con su responsabilidad, su blast radius (qué bloquea) y su
presencia en cada ruta hacia `main`. La infraestructura de aplicación se marca
explícitamente **NO-APLICA** (sin cambios respecto a la línea base).

## Inventario de componentes lógicos del gate

| Componente | Responsabilidad | Presente en PR-gate (`ci.yml` / `quality`) | Presente en push-gate (`fly-deploy.yml` / `verify`) | Blast radius (qué bloquea) |
|------------|-----------------|:---:|:---:|----------------------------|
| **Secret scanner** (`gitleaks`) | Detectar secretos filtrados en repo y tests | Sí (unificar+fijar versión) | Sí (unificar+fijar versión) | Bloquea el merge/deploy ante secreto detectado |
| **Backend dependency audit** (`pip-audit`) | Bloquear findings con fix sobre el venv instalado | Sí (promover a bloqueante) | **Añadir** (hoy ausente) | Bloquea ante CVE con fix no allowlisted |
| **Frontend dependency audit** (`npm audit --audit-level=high`) | Bloquear findings `high`+ | Sí (promover a bloqueante) | **Añadir** (hoy ausente) | Bloquea ante finding `high`+ no allowlisted |
| **Allowlist expiry check** (script) | Fallar si una excepción de la allowlist caducó | Sí | Sí | Bloquea ante entrada caducada (reactiva el bloqueo del finding) |
| **Backend lint** (`ruff check`) | Lint bloqueante (último del escalón) | Sí (quitar `continue-on-error`) | **Añadir** (hoy ausente) | Bloquea ante violación de lint no suprimida |
| **Backend coverage floor** (`pytest --cov-fail-under`) | Piso de cobertura line-only | Sí (introducir piso) | **Añadir** `--cov` + mismo piso (hoy `pytest -q` sin `--cov`) | Bloquea si la cobertura cae bajo el piso |
| **Frontend coverage ratchet** (`ng test` + `angular.json`) | Umbrales por métrica dentro de `ng test` | Sí (subir ratchet) | Sí (ya presente) | Bloquea si la cobertura cae bajo los umbrales |
| **Release verification** (`smoke-test` `/health`) | Verificar el release post-deploy | — (no aplica en PR) | Sí (sin cambios; tras deploy) | Marca el release como fallido si `/health` ≠ 200 |

## Dominios de fallo y aislamiento

- **Aislamiento por paso**: cada componente es un **step con nombre propio**
  (decisión Q3=A), de modo que su fallo es un dominio de fallo independiente —
  localizable en el log y revertible por su commit `chore(ci)` aislado sin
  arrastrar a los demás (soporta rollback quirúrgico, reliability R3).
- **Aislamiento por commit**: cada endurecimiento (promoción de un componente a
  bloqueante, pin de versión, introducción del piso) aterriza en su propio
  commit `chore(ci)`. El blast radius de un rollback es un único componente.
- **Aislamiento por ecosistema (allowlist)**: la allowlist vive en ficheros
  nativos separados backend/frontend (decisión Q1=A), de modo que una excepción
  de un ecosistema no afecta al veredicto del otro.

## Paridad de rutas (asimetría a cerrar — FR17.3)

La columna "push-gate" muestra qué componentes hay que **AÑADIR** a `verify`
(hoy sólo tiene secret scanner + `pytest -q` sin `--cov` + `ng test`): backend
audit, frontend audit, lint, `--cov` con piso, y el allowlist expiry check. Es
**añadir pasos, no flipear un flag**. El objetivo es que ningún componente del
gate falte en la ruta de push directo a `main`.

**Restricción de topología**: la cadena `needs:`
(`verify → deploy-backend → deploy-frontend → smoke-test`) **no se reordena**; se
refuerza el contenido de `verify`.

## Recurso compartido identificado

- **Entorno instalado (venv / `node_modules`)**: los componentes de audit y de
  cobertura backend/frontend comparten el entorno que instalan los pasos previos
  del job. El diseño reutiliza ese entorno (no reinstala) para respetar el
  presupuesto de tiempo (performance NFR1.2) y para que `pip-audit` audite lo que
  realmente se despliega (security C1).

## Infraestructura de aplicación — NO-APLICA (sin cambios)

Dos apps Fly.io (`futmondo-api`, `futmondo-app`), Neon PostgreSQL (Frankfurt),
crons Fly one-shot (`daily-sync.yml`, `sofascore-sync.yml`): **NO-APLICA**. Este
intent no crea, elimina ni reconfigura ningún componente de infraestructura de
aplicación; su topología es la de la línea base en producción.

## Handoff a Infrastructure Design

- No hay provisión ni cambio de infraestructura de aplicación que diseñar.
- El trabajo de infraestructura relevante es **de workflows** (config de Actions
  y `fly.toml` versionados): añadir los pasos a `verify`, pinnar tooling,
  unificar gitleaks, introducir el piso y la allowlist. Todo a coste 0 €.

## Trazabilidad

- Componentes ↔ controles de security-design (C1–C6), reliability (R3/R4),
  observability (O1/O2).

## Sources

- `./security-design.md`, `./reliability-design.md`, `./observability-design.md` (este stage).
- `../nfr-requirements/*` (NFR-SEC, NFR-REL, NFR-OBS).
- `aidlc/spaces/default/memory/team.md` §Deployment (topología, paridad, cadena `needs:`).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (stack real).

## Assumptions & Open Questions

- `functional-spec` no existe (scope infra; functional-design omitido por diseño): el contexto arquitectónico se deriva de las NFR requirements y del stack real, sin inventar contenido.
