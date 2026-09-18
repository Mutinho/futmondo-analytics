# Preguntas — Deployment Execution (Backend Security Hardening)

Scope `security-patch`, depth Minimal, brownfield, fase Operation. Esta etapa
**documenta la ejecución del despliegue y su verificación** para este release de
seguridad. El despliegue real es **on-merge a `main`** vía el pipeline Fly.io
existente (`fly-deploy.yml`); no se ejecuta un `fly deploy` manual desde aquí ni
hay entorno de staging separado.

Perspectivas integradas (topología inline): ingeniería de release (lead) y
desarrollo (developer, para migraciones de BD).

## Chequeos previos al despliegue (respondidos con evidencia existente)

- **¿Pasan todos los checks previos?** Sí. Build and Test: **135 passed, 0
  fallos, 0 regresiones** (baseline 125 → +10). Gate de CI (gitleaks + pytest +
  ng test) es bloqueante en el MR.
- **¿Se requieren migraciones de BD y están probadas?** **No.** Ninguna de las
  cinco correcciones (FR6, FR7, FR8, FR9, FR18) cambia el esquema de Neon; no
  hay pasos expand/contract ni backfill (perspectiva developer confirmada
  contra `test-results.md` y `code-summary.md`).
- **¿Servicios dependientes disponibles y sanos?** Sí. Backend `futmondo-api`
  y frontend `futmondo-app` en Fly.io (`cdg`), Neon PostgreSQL (Frankfurt). El
  healthcheck `/health` es la verificación de salud.
- **¿Ventana de despliegue?** No aplica ventana formal: despliegue on-merge a
  `main`, un solo entorno, coste 0 €. El smoke test `/health` (5 reintentos,
  HTTP 200) es la verificación de release.

## No se abren preguntas sustantivas nuevas

Las decisiones de ejecución ya están determinadas por el pipeline existente y
la evidencia de Build and Test. No aplica Q&A interactivo.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
