# CI/CD Pipeline — u1-durable-session

> Etapa Infrastructure Design (Construction). Diseño del pipeline de entrega para esta unidad sobre
> **GitHub Actions** (workflows existentes `ci.yml` y `fly-deploy.yml`). El único cambio de pipeline
> es cerrar el hueco de gitleaks en el push a `main` (Q3-A). Coste 0€.

## Sources

- team.md (`ci.yml` gate de MR bloqueante: pytest + ng test + gitleaks; `fly-deploy.yml` on-merge; hueco `verify`) [scope]
- nfr-design/security-design.md (FUTMONDO_CRED_KEY como secret; nunca literales) [scope]
- nfr-design/reliability-design.md (NFR4.1 suite verde; gate bloqueante) [scope]
- project.md (ALWAYS pasar gate CI bloqueante: gitleaks+pytest+ng test antes de fusionar) [scope]
- infrastructure-design-questions.md (Q1 SQL idempotente, Q3 gitleaks en verify, Q4 despliegue, Q6 sin migración) [Q1] [Q3] [Q4]

## Visión general

Dos disparadores, como hoy:

- **`pull_request` → `main` (`ci.yml`)**: el **gate bloqueante** de integración. Debe pasar antes de
  fusionar (branch protection).
- **push a `main` (`fly-deploy.yml`)**: verifica y **despliega** on-merge a Fly.io.

Esta unidad **reutiliza el pipeline sin cambios de estrategia** (Q4-A) y añade **un solo cambio**:
gitleaks bloqueante en el job `verify` de `fly-deploy.yml` (Q3-A), para que un secreto colado por un
push directo a `main` también se detenga (cierra el hueco relevante a FR5/NFR1.4 que team.md anotó).

## Etapas del gate de MR (`ci.yml`) — sin cambios

| Stage | Gate | Acción si falla |
|-------|------|-----------------|
| gitleaks | Escaneo de secretos | **Bloquea** el merge (bloqueante desde el inicio) |
| pytest (backend) | Suite de tests backend (incl. caracterización + nuevo contrato de durabilidad) | **Bloquea** el merge |
| ng test (frontend) | Suite Vitest | **Bloquea** el merge |
| ruff / ESLint | Lint | **Advisory** (fase de saneamiento; no bloquea todavía) |
| pip-audit / npm audit | Auditoría de dependencias | **Advisory** |

Los tests nuevos de esta unidad (caracterización de `SessionStore` y contrato de durabilidad con
**fakes de la capa de persistencia**, no Neon real) corren aquí y deben estar en verde (NFR4.1).

## Etapas del despliegue on-merge (`fly-deploy.yml`)

Orden secuencial:

1. **`verify`** — corre `pytest -q` **y ahora también gitleaks (bloqueante)** (Q3-A, cambio nuevo).
   Sigue sin `--cov` (el gap de cobertura se deja como está, fuera de alcance). Si `verify` falla,
   no se despliega.
2. **`deploy-backend`** — despliega `futmondo-api` a Fly.io (`cdg`). El **script SQL idempotente**
   (`CREATE TABLE IF NOT EXISTS`, Q1-A) se aplica al arrancar el backend, antes de servir tráfico;
   es seguro re-ejecutarlo en cada release.
3. **`deploy-frontend`** — despliega `futmondo-app` (sin cambios en esta unidad).
4. **`smoke-test`** — reintenta 5 veces contra `/health` esperando HTTP 200. Si falla, el release se
   considera fallido.

| Stage | Gate | Acción si falla |
|-------|------|-----------------|
| verify | pytest + **gitleaks (nuevo, bloqueante)** | Aborta el despliegue |
| deploy-backend | Despliegue OK + arranque (aplica SQL idempotente) | Aborta; rollback disponible |
| deploy-frontend | Despliegue OK | Aborta; rollback disponible |
| smoke-test | `/health` = 200 (5 reintentos) | Marca release fallido → rollback |

## Estrategia de despliegue y rollback

- **Estrategia:** on-merge directo a producción (sin blue-green ni canary; sin staging separado,
  Q4-A). Coherente con la topología `min=max=1` y coste 0€.
- **Rollback:** redeploy de la release anterior de Fly.io (mecanismo y runbook existentes,
  `docs/ROLLBACK.md`). El script SQL es idempotente y **aditivo** (`CREATE TABLE IF NOT EXISTS`), por
  lo que un rollback de código NO requiere deshacer el esquema: las tablas nuevas quedan huérfanas
  pero inertes (la release anterior no las usa), sin romper nada. No hay migración destructiva que
  revertir (Q6-A: no se migran datos; nunca se persiste la contraseña).

## Gestión de secretos en CI/CD

- **`FUTMONDO_CRED_KEY`** (nuevo, Q2-A): se provisiona con `fly secrets set` **fuera del repo y
  fuera de los workflows**; el CI nunca lo ve en claro. Rotación manual documentada en runbook, con
  `scheme` versionado para re-cifrado perezoso en el siguiente login.
- **`DATABASE_URL`, `JWT_SECRET`** (existentes): siguen como secrets de Fly.io / GitHub Actions,
  nunca literales en el workflow (el `JWT_SECRET` efímero de `ci.yml` es solo un literal de arranque
  no productivo, exigido por el guard NFR1.1).
- **gitleaks** actúa como red en AMBOS caminos (MR y ahora push a `main`): un secreto que se colara a
  disco/repo bloquea tanto el merge como el despliegue directo (FR5/NFR1.4).

## Promoción de entornos

No hay promoción multi-entorno: un solo entorno productivo (Q4-A). La "promoción" es el merge a
`main` que dispara el despliegue. Añadir staging queda fuera de alcance por coste (NFR3).

## Cambio concreto en `fly-deploy.yml` (ilustrativo, ≤15 líneas)

```yaml
# job verify — se añade el paso de gitleaks (bloqueante), igualándolo al gate de MR (Q3-A)
verify:
  steps:
    - uses: actions/checkout@v4
    - name: Secret scan (blocking)          # NUEVO
      uses: gitleaks/gitleaks-action@v2      # acción gratuita; sin coste
    - name: Backend tests
      run: pytest -q                          # sin --cov (gap conocido, fuera de alcance)
# deploy-backend/deploy-frontend/smoke-test: sin cambios
```

## Trazabilidad

| NFR | Solución de pipeline |
|-----|----------------------|
| NFR1.4 | gitleaks bloqueante en el gate de MR **y ahora en `verify`** del push a `main` (Q3-A); cierra el hueco de secretos por push directo |
| NFR1.2 | `FUTMONDO_CRED_KEY` provisto como secret de Fly.io fuera del repo/CI; nunca literal en workflow |
| NFR4.1 | Gate bloqueante (`pytest` + `ng test`) mantiene la suite existente verde antes de fusionar/desplegar |
| NFR5.1 | `deploy-backend` aplica el script SQL idempotente (tablas durables en Neon) antes de servir tráfico |
