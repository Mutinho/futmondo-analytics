# Reglas Descubiertas — Integración final (sólo durables transversales)

> Integración final del lead. Re-run brownfield para un intent de ANÁLISIS.
> Recoge **sólo** las reglas duras, declaradas por humanos, que son **durables y
> transversales** a cualquier intent de este proyecto, más la regla durable de
> cadena de suministro elevada en la entrevista (Q2=B). Las reglas específicas de
> intents de CI gate-hardening (FR11/FR12/FR17.3: pisos de cobertura concretos,
> promoción advisory→bloqueante, allowlist versionada con caducidad, pin de
> tooling del gate) y de refactor de god-files / manejo de errores backend **NO se
> arrastran**: no tienen efecto sobre un intent que sólo produce documentos de
> análisis.

## Mandated

- ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en
  tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free);
  descartar toda mejora o dependencia con gasto recurrente. **Excepción aceptada y
  acotada**: el **coste de publicación de distribución nativa** (Apple Developer
  Program ~99 €/año; Google Play Developer) es una excepción conocida y bounded a
  este mandato, exclusivamente para habilitar la distribución de una app nativa; el
  análisis de viabilidad lo documenta como coste recurrente de distribución. Para
  todo lo demás, el mandato de coste 0 € sigue durable y sin relajar.
- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `ruff check` + `pytest` +
  `pip-audit` + `ng test` + `npm audit`) antes de fusionar a `main`, también para
  cambios puramente documentales; un rojo nunca llega a producción.
- ALWAYS mantener el **escaneo de dependencias (`pip-audit` / `npm audit`) y de
  secretos (`gitleaks`) como control de cadena de suministro durable y
  BLOQUEANTE en AMBOS gates** (`ci.yml` job `quality` y `fly-deploy.yml` job
  `verify`), de modo que un secreto o una dependencia vulnerable nunca llegue a
  producción. (Control permanente; separado de la mecánica intent-específica de
  promoción escalonada, allowlist versionada con caducidad o pin de versiones
  concretas de tooling, que NO es una regla de equipo durable.)
- ALWAYS usar **identificadores, docstrings y comentarios en INGLÉS** y **texto
  de cara al usuario / mensajes de commit en CASTELLANO** (Conventional Commits
  con scope); en los documentos de análisis, prosa en castellano y tokens
  técnicos (frameworks, rutas, claves YAML) verbatim en inglés.

## Forbidden

- NEVER hardcodear secretos/tokens reales en el repo (código, specs, workflows ni
  documentos de análisis): los secretos van vía `secrets` de GitHub Actions /
  Fly.io y en CI el `JWT_SECRET` es efímero y no productivo (gitleaks escanea
  todo el árbol).
- NEVER introducir dependencias de pago ni servicios que fuercen salir de los
  tiers gratuitos (salvo la excepción acotada de publicación de distribución
  nativa anotada arriba); cualquier librería que se proponga en la ruta de
  implementación sería OSS y fijada a versión exacta.
- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de
  datos); cualquier modelo de sesión que proponga el análisis nativo debe
  preservar esta garantía. Al perder la cookie `HttpOnly` del navegador, el
  refresh token debe ir a **almacenamiento seguro nativo** (iOS Keychain /
  Android Keystore vía `@nativescript/secure-storage`), **NUNCA** a
  `ApplicationSettings` ni `localStorage` en claro (regla durable de seguridad,
  central al riesgo de portabilidad del modelo de sesión).
