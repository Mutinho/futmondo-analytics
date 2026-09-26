# Infrastructure Specification — Intent 4 (gate CI/CD hardening)

> Etapa de diseño: qué infraestructura se necesita y por qué, no IaC lista para
> ejecutar. Este intent es **config-only de CI/CD**: la "infraestructura" son los
> workflows de GitHub Actions y el tooling del gate; la topología de aplicación
> (Fly.io + Neon) **no cambia**. Los snippets son ilustrativos (≤15 líneas).

## Contexto de topología (SIN cambios)

`components.md` y `functional-spec.md` no existen (scope infra; domain-design y
functional-design omitidos por diseño). La topología se deriva de las NFR
requirements y del stack real, sin inventar contenido.

## Deployment

| Facet | Choice | Rationale |
|-------|--------|-----------|
| Compute model | Dos apps Fly.io (`futmondo-api` :8000 check `/health`; `futmondo-app` nginx :80 check `/`), región `cdg` — **sin cambios** | El intent no toca el runtime ni la topología de despliegue; solo endurece el gate previo. |
| Networking topology | Fly.io gestiona red/routing/TLS; TLS a Neon — **sin cambios** | Términos AWS (VPC/subnets/SG) NO-APLICAN; Fly.io lo abstrae. |
| Storage strategy | Neon PostgreSQL (Frankfurt, tier free) — **sin cambios** | BD de producción intacta; el intent no altera datos ni esquema. |
| Environments | `main` → producción on-merge; sin staging separado — **sin cambios** | El smoke test `/health` es la verificación de release; línea base afirmada. |
| IaC approach | Workflows de GitHub Actions (`ci.yml`, `fly-deploy.yml`) + `fly.toml` versionados; **este es el único material que cambia** | La infraestructura mutable de este intent es config de CI/CD, no recursos de aplicación. |
| Resource sizing | Free tier (Neon free, Fly.io free allowance, GitHub Actions free) — **sin cambios** | Restricción dura coste 0 €. |

## Infrastructure Services (del gate de CI/CD)

Los "servicios de infraestructura" relevantes son los componentes del gate,
todos OSS y a coste 0 €.

| Service | Role | Configuration | Notes |
|---------|------|---------------|-------|
| `gitleaks` (GitHub Action) | secret-scanner | Versión única fijada en `ci.yml` y `verify` (hoy `@v3` vs `@v2`) | Unificar y fijar; escanea también los tests. |
| `pip-audit` | dependency-audit (backend) | Pin exacto en el paso que lo instala; corre sobre el venv instalado (sin `-r`); bloquea findings con fix | Findings sin fix → allowlist versionada. |
| `npm audit` (built-in) | dependency-audit (frontend) | `--audit-level=high`; trinquete de severidad solo endurece | Sin dependencia nueva; no toca devDependencies. |
| `ruff check` | linter (backend) | Pin exacto; promoción a bloqueante = quitar `continue-on-error` (último del escalón) | Sin `--fix`/`ruff format` masivo. |
| `pytest` + `pytest-cov` | test + coverage-floor (backend) | `--cov-fail-under` en `pytest.ini`, line-only; misma invocación en ambos gates | Valor exacto medido en ci-pipeline. |
| `ng test` (`@angular/build:unit-test` + `@vitest/coverage-v8` pin `4.1.11`) | test + coverage-ratchet (frontend) | Umbrales en `angular.json`; `vitest` a versión exacta | Solo sube el ratchet; ya tiene paridad. |
| Allowlist expiry check | expiry-gate | Script versionado único (`scripts/`), `run:` step con nombre en ambos gates | Falla si una entrada de la allowlist caducó. |
| `smoke-test` `/health` | release-verification | 5 reintentos, HTTP 200 tras deploy — **sin cambios** | Última etapa de la cadena `needs:`. |

## Shared Infrastructure

| Shared Resource | Owner Unit | Consumer Units | Access Boundary |
|-----------------|-----------|----------------|-----------------|
| Script de expiry de la allowlist (`scripts/check-allowlist-expiry.*`) | (repo) | job `quality` (`ci.yml`) + job `verify` (`fly-deploy.yml`) | Fuente única versionada; ambos workflows lo invocan como `run:` step (Q2=A). |
| Fichero(s) de allowlist (backend ignore-vulns + equivalente npm) | (repo) | `pip-audit` / `npm audit` en ambos gates | Versionado en git, auditable; caducidad reactiva el bloqueo. |
| Entorno instalado (venv / `node_modules`) | job | pasos de audit + cobertura del mismo job | Reutilizado, no reinstalado, para respetar el presupuesto de minutos y auditar lo que se despliega. |

## Restricciones duras (preservadas)

- **Cadena `needs:` intacta**: `verify → deploy-backend → deploy-frontend →
  smoke-test`. El endurecimiento refuerza el CONTENIDO de `verify`, no reordena.
- **Deploy y crons sin cambios**: on-merge a `main`; `daily-sync.yml` /
  `sofascore-sync.yml` (máquinas Fly one-shot) intactos.
- **Coste 0 €**: sin dependencias de pago; todo OSS y en free tier.
- **Secretos**: vía `secrets` de GitHub Actions / Fly.io; `JWT_SECRET` efímero en CI.

## Trazabilidad (infra-relevante)

- NFR-SEC.1/.2/.4/.5 → tabla de servicios (audits, gitleaks, pins).
- NFR-SEC.3 → allowlist + expiry check (shared infrastructure).
- NFR-OBS.1 / NFR5.1 → misma invocación de cobertura en ambos gates; entorno instalado.
- NFR-REL.1 → cadena `needs:` intacta.
- NFR1.1 → free tier / reutilización de entorno.

## Sources

- `../nfr-design/security-design.md`, `../nfr-design/logical-components.md`, `../nfr-design/reliability-design.md` (este phase).
- `../nfr-requirements/tech-stack-decisions.md` (tooling, pins, superficies).
- `aidlc/spaces/default/memory/team.md` §Deployment (topología, cadena `needs:`, crons).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (stack real, coste 0 €).

## Assumptions & Open Questions

- `components.md` / `functional-spec.md` ausentes por diseño (scope infra); topología derivada de las NFR y del stack, sin invención.
