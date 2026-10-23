# Discovered Rules — intent 261018-design-system-nativo (RE-RUN / DRAFT)

> Sólo constraints DUROS ya establecidos y confirmados en memoria afirmada
> (`project.md` / `team.md`). Re-run: se reafirman, no se inventan reglas nuevas.

## Mandated

- ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en
  tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free);
  descartar toda mejora o dependencia con gasto recurrente. El sistema de diseño
  nativo iOS se sostiene con el **SDK de Apple** (coste 0 €), sin tooling de
  diseño de pago. **Excepción aceptada y acotada**: el coste de publicación de
  distribución nativa (Apple Developer Program ~99 €/año) es la única excepción
  conocida y bounded, sólo para habilitar la distribución de la app nativa.
- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `ruff check` + `pytest` +
  `pip-audit` + `ng test` + `npm audit`) antes de fusionar a `main`, también para
  cambios de diseño/documentales; un rojo nunca llega a producción.
- ALWAYS reproducir en **SwiftUI** (sólo SDK de Apple, coste 0 €) el tema del
  frontend Angular existente como **fuente de verdad** del diseño nativo iOS
  (`angular-app/src/styles.scss`: Material 3 paleta primaria verde, terciaria
  violeta, tipografía `Roboto`, modo claro/oscuro vía Material + `body.dark-theme`,
  tokens semánticos `money-positive`/`money-negative`, escala `h1`/`h2`/`h3`,
  gradiente de splash verde). **Google Stitch queda descartado** como referencia
  (decisión del propietario, 2026-10-18). Donde Material 3 no tenga equivalente
  1:1 en SwiftUI, cubrir con **Apple HIG** sin introducir dependencias de pago.
- ALWAYS usar **identificadores, docstrings y comentarios en INGLÉS** y **texto
  de cara al usuario / mensajes de commit en CASTELLANO** (Conventional Commits
  con scope); en la prosa de los artefactos de diseño, castellano con tokens
  técnicos verbatim en inglés.

## Forbidden

- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de
  datos); cualquier modelo de sesión del cliente nativo debe preservar esta
  garantía (el refresh token va a **almacenamiento seguro nativo** — iOS Keychain
  —, NUNCA a `localStorage` ni almacenamiento en claro).
- NEVER usar un `JWT_SECRET` por defecto en producción; el arranque del servicio
  web exige un secreto no-default (NFR1.1).
- NEVER bajar/relajar un umbral o piso de cobertura para pasar el gate; el
  ratcheting sólo sube, y el flapping se arregla en el test no-determinista.
- NEVER correr `ruff format` masivo ni `--fix` de repo entero (ni Prettier
  masivo) sobre ficheros brownfield ya modificados (infla diffs, expone avisos
  preexistentes e invalida el pase de revisión en vuelo); formatear sólo los
  ficheros nuevos o de forma quirúrgica.
- NEVER ampliar los god-files existentes (`data_sync_service.py`,
  `data_manager_v2.py`, `assistant_service.py`, `photo_service.py`) ni el patrón
  SQL-en-router; este intent de diseño no es excusa para refactor de oportunidad.
- NEVER introducir dependencias de pago ni tooling de diseño de pago; cualquier
  librería nueva sería OSS y fijada a versión exacta (no se prevé ninguna para la
  capa de diseño, que se cubre con el SDK de Apple).
