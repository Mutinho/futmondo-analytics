# NFR Design — Preguntas de diseño (Intent 4: gate CI/CD hardening)

> Etapa de **diseño** (no de implementación). Las decisiones de política ya
> afirmadas en NFR Requirements y en memoria (`team.md`/`project.md`) NO se
> re-preguntan: pip-audit bloquea findings con fix sobre el entorno instalado,
> npm audit bloquea en `high`, promoción escalonada audits→lint, piso de
> cobertura al final del escalón sin margen, gitleaks unificado y fijado,
> tooling a versión exacta, paridad PR↔push añadiendo pasos a `verify`, cadena
> `needs:` intacta, coste 0 €. Estas preguntas resuelven las decisiones de
> **diseño** que aún quedan abiertas para producir los artefactos.

---

## Q1 — Ubicación y formato de la allowlist versionada (NFR-SEC.3 / NFR-OBS.3)

La allowlist de findings sin fix debe ser un fichero versionado y auditable
(ID CVE/advisory, dependencia+versión, motivo, fecha, fecha de caducidad). El
diseño debe fijar QUÉ fichero y en qué formato, dado que pip-audit y npm
manejan la supresión de forma distinta.

- A. **Fichero único declarativo por herramienta en su ubicación nativa**: para
  pip-audit un fichero de ignore-vulns versionado (p. ej. `backend/.pip-audit-ignore`
  o equivalente pasado con `--ignore-vuln`), y para npm el mecanismo nativo
  (`.nsprc`/overrides o `audit-ci` config); cada uno junto a su ecosistema, con
  los metadatos (motivo/caducidad) como comentarios/campos en el propio fichero.
- B. **Un único documento central de excepciones** (`docs/SECURITY-ALLOWLIST.md`
  o similar) como fuente de verdad de metadatos, del que se derivan los ficheros
  nativos que consumen las herramientas.
- C. **Solo mecanismo nativo, sin metadatos estructurados** (caducidad/motivo
  como comentario suelto).
- X. Other (please specify)

[Answer]: A

---

## Q2 — Enforcement de la caducidad de la allowlist (NFR-SEC.3)

"Una entrada caducada vuelve a bloquear" es un requisito. ¿Cómo se diseña ese
enforcement a coste 0 €?

- A. **Chequeo determinista en el propio gate**: un paso ligero (script en el
  workflow) compara la fecha de caducidad de cada entrada con la fecha actual y
  falla el job si alguna está caducada, ANTES o junto al audit. Cero
  dependencias de pago.
- B. **Revisión manual periódica** (recordatorio documentado), sin enforcement
  automático en el gate.
- C. **Herramienta de terceros** que gestione caducidad nativamente.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Presentación del modo de fallo del gate (fiabilidad/observabilidad, NFR-OBS.2)

Cuando un check promovido a bloqueante falla, ¿qué patrón de diseño se aplica
para que el fallo sea diagnosticable y no un rojo opaco?

- A. **Cada check como paso identificable y aislado** con nombre explícito
  (`pip-audit (blocking)`, `npm audit (high, blocking)`, `ruff check (blocking)`,
  `coverage floor`), fallando de forma independiente para localizar la causa sin
  leer todo el log; sin agrupar en un único paso monolítico.
- B. **Un paso agregado "security gate"** que corre todo y reporta el conjunto.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Modelo del artefacto `logical-components.md` para un intent config-only

Este intent no despliega componentes de aplicación nuevos; los "componentes
lógicos" son los del **propio gate**. ¿Cómo se enfoca `logical-components.md`?

- A. **Componentes lógicos del gate como dominios de fallo**: modelar el gate
  como componentes (escáner de secretos, audit de dependencias backend, audit
  frontend, lint, piso de cobertura, verificación de release/smoke test) con su
  blast radius (qué bloquea cada uno) y su paridad PR↔push, y marcar
  explícitamente NO-APLICA los componentes de infraestructura de aplicación
  (sin cambios respecto a la línea base).
- B. **Inventario mínimo** que solo remita a la topología de producción existente
  y declare el intent como sin nuevos componentes lógicos.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Alcance de la medición previa del piso de cobertura (NFR5.2, coordinación con ci-pipeline)

La política del piso ya está afirmada (valor medido exacto, line-only, sin
margen, al final del escalón). ¿El diseño debe fijar aquí el VALOR numérico o
solo el mecanismo, dejando la medición para ci-pipeline?

- A. **Solo el mecanismo y la política** en este artefacto (único
  `--cov-fail-under` en `pytest.ini`, paridad en `verify`), remitiendo la
  medición del valor exacto a ci-pipeline sobre la suite estabilizada — evita
  fijar un número que quede obsoleto.
- B. **Medir y fijar el valor numérico aquí** como parte del diseño.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de diseño que se van a plasmar en los artefactos:

- **Q1 — Allowlist (A)**: fichero nativo por herramienta (pip-audit vía
  `--ignore-vuln` en fichero versionado; npm vía su mecanismo nativo), con
  metadatos (ID CVE/advisory, dependencia+versión, motivo, fecha, caducidad) en
  el propio fichero. Auditable en git, coste 0 €.
- **Q2 — Caducidad (A)**: enforcement determinista en el gate — un paso ligero
  falla el job si alguna entrada de la allowlist está caducada. Sin dependencias
  de pago.
- **Q3 — Modo de fallo (A)**: cada check bloqueante como paso identificable y
  aislado con nombre explícito, fallando de forma independiente (diagnóstico
  directo, rollback quirúrgico, NFR-OBS.2).
- **Q4 — `logical-components.md` (A)**: modelar el gate como componentes/dominios
  de fallo (escáner de secretos, audit backend, audit frontend, lint, piso de
  cobertura, verificación de release) con su blast radius y su paridad PR↔push;
  NO-APLICA para la infraestructura de aplicación (sin cambios).
- **Q5 — Piso de cobertura (A)**: el artefacto fija el mecanismo y la política
  (único `--cov-fail-under` en `pytest.ini`, line-only, paridad en `verify`); el
  VALOR numérico se mide en ci-pipeline sobre la suite estabilizada.

Se generarán 7 artefactos: `performance-design.md`, `security-design.md`,
`scalability-design.md`, `reliability-design.md`, `observability-design.md`,
`logical-components.md` y `traceability.json`, respetando el mandato coste 0 €,
la adaptación Fly.io/GitHub Actions y todas las reglas afirmadas.

[Answer]: Looks correct
