# Evidencia — practices-discovery F1 (login nativo iOS)

> Etapa: inception (practices-discovery). Intent: `261016-f1-login-nativo`.
> Idioma: castellano; tokens técnicos verbatim en inglés.
>
> Evidencia que respalda (A) el **reconocimiento** de las prácticas ya afirmadas
> aplicables a F1 (`team-practices.md`) y (B) las **propuestas nuevas**
> (`discovered-rules.md`). Las citas apuntan al codekb de reverse-engineering, a
> los ficheros de `memory/` y a los artefactos de ideación de F1.

## A. Evidencia del reconocimiento de lo YA AFIRMADO

### A.1 Coste 0 € y excepción de distribución nativa
- `aidlc/spaces/default/memory/project.md` → `## Mandated`: "ALWAYS mantener el
  proyecto a **coste 0 €** … **Excepción aceptada y acotada**: el coste de
  publicación de distribución nativa (Apple Developer Program ~99 €/año…)".
- `aidlc/spaces/default/memory/team.md` → `## Deployment`: "Restricción dura
  (durable) y su excepción acotada (Q1=B)".
- Respaldo en codekb: `codekb/futmondo-analytics/dependencies.md` →
  "Todas sostenibles en tiers gratuitos (mandato coste 0 €). La única excepción
  acotada … Apple Developer Program".

### A.2 Gate de CI bloqueante
- `codekb/futmondo-analytics/code-quality-assessment.md` → `## Gate de CI
  (bloqueante)`: tabla de pasos (`gitleaks @v3`, `ruff check` 0.16.9, `pytest`
  `--cov-fail-under=27`, `pip-audit` 2.10.1, `ng test` Vitest, `npm audit
  --audit-level=high`) replicados en `ci.yml` (job `quality`) y `fly-deploy.yml`
  (job `verify`).
- `aidlc/spaces/default/memory/project.md` → `## Mandated`: "ALWAYS pasar el gate
  de CI bloqueante (gitleaks + ruff check + pytest + pip-audit + ng test + npm
  audit) antes de fusionar a `main`, también para cambios puramente documentales".
- Trazado a F1: `ideation/feasibility/constraint-register.md` → C-05.

### A.3 Way of Working (trunk-based + squash + Conventional Commits)
- `aidlc/spaces/default/memory/team.md` → `## Way of Working`: "trunk-based …
  squash-merge a `main` … Conventional Commits con scope entre paréntesis y en
  castellano".
- `aidlc/spaces/default/memory/org.md` → `## Way of Working`: base `main`,
  target `main`, squash-merge.

### A.4 Idioma del código y de cara al usuario
- `aidlc/spaces/default/memory/project.md` → `## Mandated`: "ALWAYS usar
  identificadores, docstrings y comentarios en INGLÉS y texto de cara al
  usuario / mensajes de commit en CASTELLANO".
- `aidlc/spaces/default/memory/team.md` → `## Code Style`: "Idioma en el código
  (durable): identificadores/docstrings/comentarios en INGLÉS; texto de usuario y
  commits en CASTELLANO".
- Trazado a F1: `constraint-register.md` → C-04.

### A.5 Seguridad de credenciales (Keychain, JWT_SECRET, no-claro)
- `aidlc/spaces/default/memory/project.md` → `## Forbidden`: "NEVER almacenar la
  contraseña Futmondo en claro …", "NEVER usar un `JWT_SECRET` por defecto en
  producción", "el refresh token debe ir a **almacenamiento seguro nativo** (iOS
  Keychain / Android Keystore …), **NUNCA** a `ApplicationSettings` ni
  `localStorage` en claro".
- Respaldo en codekb: `codekb/futmondo-analytics/architecture.md` → "Modelo de
  autenticación (clave para F1)": access token en memoria; refresh token hoy
  **sólo** cookie `HttpOnly` (`_set_refresh_cookie`, `futmondo_refresh_token`,
  `path="/auth"`, `samesite=lax`); JWT HS256 (`jwt_utils.py`).
- `code-quality-assessment.md` → "Seguridad de credenciales": password nunca en
  memoria (`session_store.UserSession`); JWT fail-fast (`test_jwt_startup.py`,
  NFR1.1); `integration_errors.py` no acepta material de credencial (NFR3).
- Trazado a F1: `constraint-register.md` → C-02, C-06; `raid-log.md` → R-02.

### A.6 Testing posture (test-after, aserción de efecto, fakes, ratchet)
- `aidlc/spaces/default/memory/team.md` → `## Testing Posture`: "Methodology:
  test-after … tests que aseveran el efecto … fixtures fake in-memory sin red,
  sin BD real y sin credenciales/tokens reales … el trinquete de cobertura sólo
  sube".
- Respaldo en codekb: `code-quality-assessment.md` → "Suite de tests existente"
  (backend characterization-first ~50+ `test_*.py`, con auth
  `test_auth_characterization.py`, `test_jwt_startup.py`; frontend specs de auth
  `auth.service.spec.ts`, `auth.interceptor.spec.ts`, `auth.guard.spec.ts`);
  "Pisos de cobertura heredados" (backend `--cov-fail-under=27`; frontend
  `statements 19 / branches 19 / functions 17 / lines 18`).

### A.7 Brownfield (characterization-first, no ampliar god-files)
- `aidlc/spaces/default/memory/project.md` → `## Forbidden`/`## Mandated`:
  "NEVER ampliar los god-files existentes (`data_sync_service.py`,
  `data_manager_v2.py`) ni el patrón SQL-en-router"; "ALWAYS caracterizar
  (congelar con tests) el comportamiento brownfield antes de endurecerlo".
- Respaldo en codekb: `code-structure.md` → "God-files heredados (deuda conocida
  — NO ampliar)" y `code-quality-assessment.md` → "God-files como deuda conocida".

### A.8 Despliegue on-merge a Fly.io
- `aidlc/spaces/default/memory/team.md` → `## Deployment`: "Desplegamos on-merge a
  `main` hacia Fly.io (región `cdg`) … smoke test contra `/health` …
  `verify → deploy-backend → deploy-frontend → smoke-test`".
- Respaldo en codekb: `architecture.md` → "Despliegue y CORS" (dos apps Fly.io).

## B. Evidencia de las PROPUESTAS nuevas

### B.1 (P-1) No hay arnés de test iOS; verificación manual en iPhone 13 Pro; XCTest como deuda
- `ideation/scope-definition/scope-document.md` → "Definición de hecho":
  "Cliente nativo: validación manual documentada en el iPhone 13 Pro
  (login → refresh → logout); arnés de test de UI/dispositivo nativo como deuda
  registrada".
- Precedente de deuda diferida de tooling de test:
  `aidlc/spaces/default/memory/project.md` → `## Forbidden` ("NEVER instalar
  ESLint … ESLint frontend queda como **deuda diferida**") y
  `code-quality-assessment.md` → nota de ESLint advisory/diferido.
- Portabilidad de posture (suelo nuevo bajo tooling distinto, no trinquete que
  arrastre): `team.md` → `## Testing Posture`, "Portabilidad de la posture al
  target nativo".

### B.2 (P-2) D-01 aditivo, cubierto por `pytest`, sin romper el canal cookie
- `codekb/futmondo-analytics/architecture.md` → "Refresh token … **No** existe
  hoy ningún transporte del refresh token por body o header — ese es el ajuste
  aditivo D-01 que F1 necesita para iOS"; "D-01 (transporte del refresh fuera de
  cookie) evita la dependencia de CORS+cookies".
- `codekb/futmondo-analytics/business-overview.md` → "Relevancia para F1":
  "transporte alternativo del refresh token (decisión D-01, ajuste **aditivo** del
  backend) … El flujo de negocio se mantiene; F1 sólo cambia el canal de
  transporte".
- `ideation/scope-definition/scope-document.md` → "Dentro de alcance" §1:
  "sin romper el canal cookie `HttpOnly` de la PWA. Con tests `pytest`".
- `ideation/feasibility/constraint-register.md` → C-03; `raid-log.md` → R-01,
  D-01, A-01/A-02 (JWT estándar y Bearer ya validado, confirmados por
  `jwt_utils.py`/`dependencies.py`).
- Red de characterization sobre la que se añade:
  `code-quality-assessment.md` → "Auth: `test_auth_characterization.py`,
  `test_jwt_startup.py`, `test_token_store_migrations.py`".

### B.3 (P-3) Dependencias nativas: sólo SDK de Apple, cero terceros
- `ideation/scope-definition/scope-document.md` → "Dentro de alcance" §4:
  "Polish nativo de la UI de login (**SwiftUI puro, sin dependencias externas**)";
  "Face ID / Touch ID (`LocalAuthentication`) → mejora opcional **diferida**".
- `ideation/feasibility/constraint-register.md` → C-01: "El cliente usa SDK
  (URLSession, Keychain); sin librerías de pago."
- `codekb/futmondo-analytics/technology-stack.md` → "Relevancia para F1":
  "El almacén seguro nativo previsto para el refresh token es iOS Keychain …
  para Swift nativo el equivalente es Keychain directo".
- `aidlc/spaces/default/memory/project.md` → `## Mandated` (OSS pin exacto, sin
  dependencias de pago) y la excepción acotada de distribución nativa.

### B.4 (P-4) Scope de commit e idioma para Swift
- `ideation/feasibility/constraint-register.md` → C-04 ("Aplica al cliente Swift
  y al ajuste de backend").
- `aidlc/spaces/default/memory/team.md` → `## Way of Working` (Conventional
  Commits con scope en castellano) y `## Code Style` (idioma del código).

## Sources

- codekb: `aidlc/spaces/default/codekb/futmondo-analytics/{business-overview,
  technology-stack,dependencies,architecture,code-structure,code-quality-assessment}.md`.
- memory: `aidlc/spaces/default/memory/{org,team,project}.md`.
- ideación F1: `aidlc/spaces/default/intents/261016-f1-login-nativo/ideation/
  {scope-definition/scope-document.md,feasibility/constraint-register.md,
  feasibility/raid-log.md,intent-capture/intent-statement.md}`.
- Ficheros de repo citados por el codekb (no re-abiertos en esta etapa):
  `backend/app/auth/{routes,jwt_utils,dependencies,session_store}.py`,
  `backend/pytest.ini`, `backend/ruff.toml`, `.github/workflows/{ci,fly-deploy}.yml`,
  `angular-app/src/app/core/services/auth.service.ts`.

## Assumptions & Open Questions

- Las citas a ficheros de código del repo (`auth/routes.py`, `jwt_utils.py`,
  etc.) se toman del codekb de reverse-engineering (verificado en esa etapa), no
  de una re-lectura línea a línea en esta etapa de practices-discovery; el codekb
  es la fuente intermedia para evitar re-escanear el repo.
