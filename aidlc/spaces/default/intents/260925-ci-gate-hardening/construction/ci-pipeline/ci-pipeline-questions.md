# CI Pipeline — Preguntas (Intent 4: gate CI/CD hardening)

> Etapa terminal de Construction para el scope infra. El CI tool (GitHub
> Actions), la branch strategy (trunk-based, squash a `main`), y las quality
> gates están ya afirmados y diseñados en las etapas previas (NFR Design,
> Infrastructure Design). Estas preguntas cierran las decisiones concretas de
> **configuración del pipeline** que quedan para materializar `ci-config.md` y
> `quality-gates.md`, sin re-preguntar lo ya decidido.

---

## Q1 — Convención de pin de versiones del tooling del gate

Las reglas exigen pin a versión exacta en el paso que instala cada herramienta.
¿Qué convención concreta se documenta para `ruff` y `pip-audit` (hoy
`pip install ruff` / `pip install pip-audit` sin pin) y para `gitleaks-action`
(hoy `@v3` vs `@v2`)?

- A. **Pin a versión exacta por número** para las herramientas pip
  (`pip install ruff==X.Y.Z`, `pip-audit==X.Y.Z`) y **gitleaks-action a un tag de
  versión mayor único fijado** (`@v2` en ambos gates, la versión que ya corre en
  `verify`), documentando que el pin por SHA de acciones de terceros mutables se
  aborda como endurecimiento adicional en el mismo intent si el equipo lo desea.
- B. **Pin por SHA** de TODAS las acciones (incluida gitleaks) ya en esta etapa.
- C. Dejar el número concreto abierto y solo documentar la política.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Unificación de la versión de gitleaks (qué versión gana)

Hoy `ci.yml` usa `gitleaks/gitleaks-action@v3` y `verify` usa `@v2`. Al
unificar, ¿cuál se adopta en ambos gates?

- A. **Unificar a `@v2`** (la que ya corre en el push-gate `verify`), por ser la
  probada en la ruta de deploy; documentar la decisión y dejar el salto a `@v3`
  como cambio aislado posterior si se valida.
- B. **Unificar a `@v3`** (la del PR-gate), como versión más reciente.
- C. Fijar por SHA una versión concreta, sin preferir tag mayor.
- X. Other (please specify)

[Answer]: B

---

## Q3 — Formato del fichero de allowlist de pip-audit

Para materializar la allowlist versionada (findings sin fix), ¿qué formato de
fichero para el backend?

- A. **Fichero de texto versionado con columnas** (`# CVE  dependencia  versión
  motivo  fecha  caducidad`), consumido por el script de expiry y por
  `pip-audit --ignore-vuln <ID>` (los IDs se extraen del mismo fichero). Legible,
  auditable en git, sin dependencia extra.
- B. **Fichero de configuración nativo de pip-audit** si existe uno estándar
  para ignore-vulns, con los metadatos como comentarios.
- C. **JSON/TOML estructurado** parseado por el script.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Verificación de frontera Construction→Operation en scope infra

El Step 5 del stage lee traceability de code-generation/build-and-test, que
**no existen** en scope infra (omitidos por diseño). ¿Cómo se resuelve el
veredicto de frontera?

- A. **Veredicto adaptado**: documentar en `phase-check-construction.md` que
  code-generation y build-and-test se omitieron por diseño del scope infra
  (config-only, sin código de aplicación nuevo), que el "código" a verificar son
  los workflows/config versionados, y que las quality gates de este intent
  ENDURECEN la verificación existente. Confirmar que el gate ya operativo
  (gitleaks + pytest + ng test) pasa en verde como línea base. Sin fabricar
  traceability inexistente.
- B. **Saltar la verificación de frontera** por completo (no aplica).
- X. Other (please specify)

[Answer]: A

---

## Q5 — Alcance de `ci-config.md` frente a lo ya diseñado

`cicd-pipeline.md` (Infrastructure Design) ya documentó el pipeline endurecido.
¿Qué añade `ci-config.md` en esta etapa?

- A. **La configuración concreta y accionable**: el diff exacto por fichero
  (`ci.yml`, `fly-deploy.yml`, `pytest.ini`, `angular.json`, `requirements.txt`,
  allowlist + script), la secuencia de commits `chore(ci)`, y los valores de pin
  — es decir, el "cómo" ejecutable que `cicd-pipeline.md` dejó a nivel de diseño.
  `quality-gates.md` recoge las quality gates con su criterio pass/fail.
- B. **Resumen que remite a `cicd-pipeline.md`** sin detalle accionable nuevo.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de configuración del pipeline:

- **Q1 — Pin de tooling (A)**: pin exacto por número para `ruff` y `pip-audit` en
  el paso que los instala; `gitleaks-action` a un tag mayor único fijado. Pin por
  SHA de todas las acciones como endurecimiento opcional documentado, no forzado.
- **Q2 — gitleaks unificado (B)**: unificar a `@v3` en ambos gates; el push-gate
  sube de `@v2` a `@v3`.
- **Q3 — Allowlist (A)**: fichero de texto versionado con columnas, fuente única
  del script de expiry y de `pip-audit --ignore-vuln`.
- **Q4 — Frontera Construction→Operation (A)**: veredicto adaptado — code-generation
  y build-and-test omitidos por diseño del scope infra; verificar que el gate base
  pasa en verde y que este intent lo endurece; sin fabricar traceability.
- **Q5 — `ci-config.md` (A)**: configuración concreta y accionable (diff por
  fichero, secuencia de commits `chore(ci)`, pins); `quality-gates.md` con
  criterio pass/fail por gate.

Se generarán: `ci-config.md`, `quality-gates.md` y el veredicto de frontera
`verification/phase-check-construction.md`, respetando el mandato coste 0 €,
la cadena `needs:` intacta y todas las reglas afirmadas.

[Answer]: Looks correct
