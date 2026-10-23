# Practices Discovery — Timestamp

- **Date**: 2026-10-20
- **Stage**: practices-discovery (Inception)
- **Intent**: F3 Mercado — `261020-mercado-pujas` (brownfield, UI nativa iOS)
- **Agent**: aidlc-pipeline-deploy-agent (release engineer)
- **Tipo de descubrimiento**: **confirmación de prácticas vigentes**, no
  reinvención.

## Alcance

Confirmación de prácticas vigentes para **F3 Mercado** (pantalla nativa iOS en
SwiftUI que reproduce la vista Angular de Mercado como 2ª pestaña del `TabView`
tras Presupuesto, con lectura + escritura pujar/cancelar + detalle Sofascore,
sin cambios de backend), **sin reglas nuevas**. Se verificó que las prácticas
afirmadas en `org.md` / `team.md` / `project.md` aplican a F3 y que la novedad de
F3 (escritura y 2º endpoint externo) **refuerza** las reglas de seguridad ya
afirmadas, sin contradecir la política más amplia (`org → team → project`).

## Resultado

- Prácticas confirmadas: way of working (trunk-based + squash-merge +
  Conventional Commits castellano), walking skeleton **OFF**, testing posture
  **test-after** (con el matiz nativo iOS: `FutmondoKit` + XCTest, vistas SwiftUI
  en dispositivo, `llvm-cov` no fiable en WSL), deployment Fly.io on-merge (F3 no
  despliega), code style/idioma (identificadores en inglés / texto de usuario en
  castellano), coste 0 € (solo SDK de Apple), fuente de verdad del diseño
  (tema Angular Material 3 + Apple HIG; Google Stitch descartado), y seguridad
  (refresh token en Keychain, access token en memoria, errores tipados sin
  credenciales, `JWT_SECRET` no-default).
- **Reglas nuevas a proponer a memoria: NINGUNA.**

## Intents previos que ya afirmaron estas prácticas

- **F1** `261018-design-system-nativo` — afirmó sistema de diseño nativo iOS,
  tema Angular como fuente de verdad, SDK de Apple (coste 0 €), Color Sets en
  código, cobertura `llvm-cov` no fiable en WSL → `FutmondoKit` + XCTest
  (aprendizajes durables en `project.md`, 2026-10-18/19).
- **F2** `261019-presupuesto-selector-cam` — primera feature de datos nativa
  (lectura), consolidó la separación `FutmondoKit`/`FutmondoApp` y el refresco de
  CodeKB de la capa `ios/`.
- **Intents de backend/CI gate-hardening** (2026-09) — afirmaron el gate de CI
  bloqueante (gitleaks + ruff check + pytest + pip-audit + ng test + npm audit),
  pisos de cobertura (ratchet solo sube), coste 0 €, `JWT_SECRET` no-default,
  no-almacenar-credenciales-en-claro, y no-ampliar god-files.

## Sources

- `aidlc/spaces/default/memory/{org,team,project}.md`.
- `aidlc/spaces/default/intents/261020-mercado-pujas/inception/practices-discovery/`
  — `team-practices.md`, `discovered-rules.md`, `evidence.md`.
- `aidlc/spaces/default/codekb/futmondo-analytics/` (CodeKB).
- Intents previos: `261018-design-system-nativo`,
  `261019-presupuesto-selector-cam`, y los intents de backend/CI de 2026-09.

## Assumptions & Open Questions

None.
