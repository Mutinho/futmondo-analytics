# Prácticas de equipo/proyecto YA AFIRMADAS aplicables a F1

> Etapa: inception (practices-discovery). Intent: `261016-f1-login-nativo`
> (F1: login nativo iOS Swift/SwiftUI contra el backend FastAPI existente).
> Idioma: castellano; tokens técnicos verbatim en inglés.
>
> **Alcance de este fichero**: reconocer, NO re-descubrir. El proyecto Futmondo
> Analytics ya tiene prácticas de equipo y proyecto afirmadas y durables en
> `aidlc/spaces/default/memory/team.md` y `project.md`. Aquí se listan **sólo las
> vigentes que aplican a F1**, con su origen, marcadas como ya en vigor. Las
> propuestas nuevas o específicas de F1 van en `discovered-rules.md`, no aquí.

## Resumen

Todas las reglas de esta sección están **VIGENTES** (ya afirmadas; no requieren
re-afirmación). F1 las hereda tal cual: ningún punto de abajo es una propuesta.

### 1. Coste 0 € (VIGENTE — `project.md` / `team.md`, Mandated/Deployment)

- Todo en **tiers gratuitos** (Neon free, Fly.io free allowance, GitHub Actions
  free); se descarta toda mejora o dependencia con gasto recurrente.
- **Excepción acotada ya afirmada**: el coste de **publicación de distribución
  nativa** (Apple Developer Program ~99 €/año; Google Play Developer) es una
  excepción conocida y *bounded* a este mandato, exclusivamente para habilitar la
  distribución de una app nativa. Para todo lo demás el mandato de coste 0 €
  sigue durable y sin relajar.
- **Aplicación a F1**: el cliente Swift y el ajuste de backend no introducen
  dependencias de pago (ver reglas de dependencias nativas en `discovered-rules.md`,
  que son especialización, no relajación).

### 2. Gate de CI bloqueante (VIGENTE — `team.md` Way of Working / `project.md` Mandated)

- Antes de fusionar a `main` (también para cambios puramente documentales) pasa
  el **gate de CI bloqueante**: `gitleaks` + `ruff check` + `pytest` +
  `pip-audit` + `ng test` + `npm audit`. Un rojo nunca llega a producción.
- Replicado en **ambos** gates: `.github/workflows/ci.yml` (job `quality`,
  `pull_request → main`) y `.github/workflows/fly-deploy.yml` (job `verify`,
  `push → main`); los `needs:` no cruzan workflows, por eso se replica.
- `gitleaks` fijado a una única versión en ambos gates; `ruff`/`pip-audit`/
  `vitest` pineados a versión exacta en el paso que los instala.
- **Aplicación a F1**: el ajuste aditivo del backend (D-01) trae `pytest` y pasa
  el gate completo antes de `main` (ver C-05 del constraint-register).

### 3. Way of Working — trunk-based + squash-merge + Conventional Commits (VIGENTE — `team.md`)

- **trunk-based development** sobre `main`, ramas cortas con prefijo por tipo
  (`fix/...`, `chore/...`, `feat/...`, `docs/...`), integración por Pull Request
  con el gate de CI como required status check.
- **squash-merge** a `main` (cada PR = un único commit; base de worktree `main`,
  destino `main`), alineado con `org.md`.
- **Conventional Commits** con scope entre paréntesis y en castellano
  (`feat(ios-auth)`, `feat(auth)`, `chore(ci)`…).
- **Aplicación a F1**: tanto el cliente Swift como el ajuste de backend siguen
  esta política sin cambios.

### 4. Idioma del código y de cara al usuario (VIGENTE — `team.md` / `project.md` / `org.md`)

- **Identificadores, docstrings y comentarios en INGLÉS**; **texto de cara al
  usuario** (`HTTPException.detail`, prosa de UI) y **mensajes de commit** en
  **CASTELLANO** (Conventional Commits con scope).
- En documentos de análisis: prosa en castellano, tokens técnicos (frameworks,
  rutas, claves YAML/enums) verbatim en inglés.
- **Aplicación a F1**: el código Swift usa identificadores/comentarios en inglés;
  los textos visibles del login (`SwiftUI`) y los commits, en castellano
  (ver C-04 del constraint-register).

### 5. Seguridad de credenciales (VIGENTE — `project.md` Forbidden/Mandated)

- **NUNCA** almacenar la contraseña Futmondo en claro (ni en memoria ni en base
  de datos).
- Al perder la cookie `HttpOnly` del navegador en un cliente nativo, el refresh
  token va a **almacenamiento seguro nativo** (iOS Keychain / Android Keystore),
  **NUNCA** a `ApplicationSettings` ni `localStorage` en claro — regla durable de
  seguridad, central al riesgo de portabilidad del modelo de sesión.
- **NUNCA** usar un `JWT_SECRET` por defecto en producción; arranque fail-fast
  (NFR1.1, endurecido en `test_jwt_startup.py`); secretos vía `secrets` de GitHub
  Actions / Fly.io; en CI el `JWT_SECRET` es efímero y no productivo.
- **NUNCA** incluir material de credencial (password, token) en el mensaje,
  `repr`, `args` ni `exc_info` de una excepción de integración.
- **Aplicación a F1**: refresh token en **iOS Keychain**, access token sólo en
  memoria, borrado del Keychain en logout (ver C-02, R-02 del RAID).

### 6. Testing posture — test-after, aserción de efecto, fakes in-memory, ratchet (VIGENTE — `team.md` / `project.md`)

- **Methodology**: test-after. Tests como entregable de primera clase que
  **aseveran el efecto** (payload/estado/modo de fallo), nunca `assert True` ni
  specs espejo.
- Fixtures **fake in-memory** (patrón `conftest.py`), sin red, sin DB real y sin
  credenciales/tokens reales (gitleaks escanea también los tests).
- **Trinquete de cobertura que SÓLO sube**: backend `--cov-fail-under` en
  `pytest.ini` (hoy `27`, line-only); frontend `coverageThresholds` en
  `angular.json`. Nunca bajar un umbral para pasar el gate; el flapping se arregla
  en el test no-determinista.
- **Aplicación a F1 (sobre el ajuste de backend)**: la suite backend sigue en
  verde, los tests de D-01 aseveran efecto y se respeta el ratchet. (La posture
  del cliente **nativo Swift**, hoy inexistente, se trata como PROPUESTA en
  `discovered-rules.md`, porque la posture afirmada se midió sobre `pytest`/
  `Vitest`, no sobre XCTest.)

### 7. Brownfield — characterization-first y no ampliar god-files (VIGENTE — `project.md` / `team.md`)

- **characterization-first**: congelar con tests el comportamiento brownfield
  antes de endurecerlo/cambiarlo.
- **NUNCA ampliar** los god-files existentes (`data_manager_v2.py`,
  `data_sync_service.py`, `assistant_service.py`, `photo_service.py`) ni el patrón
  SQL-en-router; el código nuevo va tras una capa/función estrecha testeable.
- **NUNCA** `ruff format` en masa ni `--fix` de repo entero sobre ficheros
  brownfield ya modificados; formatear sólo ficheros nuevos o de forma
  quirúrgica.
- **Aplicación a F1**: D-01 toca `auth/routes.py`/`jwt_utils.py`/`models.py`; el
  cambio es estrictamente aditivo y no amplía god-files ni reformatea en masa; el
  contrato de auth ya tiene red de characterization (`test_auth_characterization.py`,
  `test_jwt_startup.py`).

### 8. Despliegue on-merge a Fly.io (VIGENTE — `team.md` Deployment)

- **Deploy on-merge** a `main` hacia Fly.io (región `cdg`), sin staging separado;
  smoke test contra `/health` como verificación del release
  (`verify → deploy-backend → deploy-frontend → smoke-test`).
- **Aplicación a F1**: el ajuste de backend se despliega por el pipeline
  existente; el cliente nativo iOS NO se despliega por Fly.io (su distribución es
  la cadena `xtool`/Apple, fuera del pipeline web).

## Sources

- `aidlc/spaces/default/memory/team.md` (Way of Working, Testing Posture,
  Deployment, Code Style, Mandated, Forbidden).
- `aidlc/spaces/default/memory/project.md` (Mandated, Forbidden, Corrections,
  Code Style).
- `aidlc/spaces/default/memory/org.md` (Way of Working, Testing Posture,
  Deployment, Mandated — idioma de conversación).
- `aidlc/spaces/default/intents/261016-f1-login-nativo/ideation/feasibility/constraint-register.md`
  (C-01…C-08: la trazabilidad de qué regla durable aplica a F1).
- `aidlc/spaces/default/codekb/futmondo-analytics/code-quality-assessment.md`
  (gate de CI operativo, pisos de cobertura, god-files, red de tests de auth).

## Assumptions & Open Questions

None.
