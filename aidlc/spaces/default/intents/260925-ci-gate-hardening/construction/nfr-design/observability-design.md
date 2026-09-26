# Observability Design — Intent 4 (gate CI/CD hardening)

> Etapa de diseño: patrones y decisiones, no implementación. Adaptado al stack
> real (GitHub Actions + Fly.io) y al mandato coste 0 €.

## Alcance

La observabilidad relevante es la **de la señal del gate**: qué ve el equipo
cuando el gate corre. No se introduce tracing distribuido, SLO formales con
burn-rate ni anomaly detection ML (exigirían servicios de pago); se documenta la
alternativa gratuita en su lugar (regla de adaptación Fly.io/coste 0 €).

## Diseño de observabilidad del gate

### O1 — Señal de cobertura backend visible en ambos gates (NFR-OBS.1)

- La cobertura backend con piso se **reporta y bloquea** tanto en `ci.yml` (PR,
  job `quality`) como en el job `verify` (push), usando la **misma invocación**
  de `pytest --cov` con el mismo `--cov-fail-under`.
- Así el estado de cobertura es observable en **cualquier ruta hacia `main`**,
  cerrando la asimetría actual (`ci.yml` mide `--cov`; `verify` corre `pytest -q`
  sin `--cov`).

### O2 — Estado de audits/lint observable como paso propio (NFR-OBS.2, Q3=A)

- Cada control bloqueante aparece como un **paso identificable con nombre
  explícito** en el log del workflow, con su resultado (pass/fail) visible:
  `pip-audit (blocking)`, `npm audit (high, blocking)`, `ruff check (blocking)`,
  `coverage floor`, `allowlist expiry check`.
- Los pasos **no se ocultan tras `continue-on-error`** una vez promovidos, y
  **no se agrupan** en un único paso monolítico: el fallo es localizable sin leer
  todo el log (patrón de dominios de fallo, ver logical-components).

### O3 — Trazabilidad de excepciones de seguridad (NFR-OBS.3)

- La **allowlist versionada** (findings sin fix) es observable en git: qué se
  aceptó, por qué y **hasta cuándo** (fecha de caducidad). El chequeo determinista
  de caducidad (security-design C4) emite un `::error::` con el ID del advisory,
  la dependencia y la fecha cuando una entrada caduca, de modo que el motivo del
  bloqueo es autoexplicativo en el log.

### O4 — Verificación de release intacta (NFR-OBS.4)

- El smoke test contra `/health` (5 reintentos, HTTP 200) sigue siendo la señal
  de éxito del release.
- Herramientas de observabilidad de runtime gratuitas ya existentes: `fly logs`,
  `fly status` y el healthcheck `/health`. Se preferirán **logs estructurados**
  (campos como `sync_step`, `reason`, `task_id`) para que `fly logs` + `grep`
  sustituyan a consultas gestionadas — pero esto es contexto de runtime, no lo
  cambia este intent.

### O5 — Consumo de free tier documentado (NFR6.1)

- El consumo de minutos de GitHub Actions (y su margen frente al allowance
  gratuito) queda **documentado** como observabilidad de coste (cuantificación en
  FR16, ci-pipeline). Es la sustitución gratuita de Cost Explorer/Trusted
  Advisor: el mandato de coste 0 € verificado por diseño.

### O6 — No reformateo brownfield preserva la señal de revisión (NFR3.1)

- Ningún endurecimiento ejecuta `ruff format`/Prettier en masa sobre ficheros
  heredados; sólo ficheros nuevos o cambios quirúrgicos. Criterio observable: el
  **diff de cada commit `chore(ci)` no contiene reflow ajeno** al cambio, de modo
  que la señal de la reviewer (que sólo corre `ruff check`, no `format`) se
  mantiene estable durante su pasada.

### O7 — Idioma de artefactos y commits (NFR6.2)

- Identificadores/docstrings/comentarios en **inglés**; texto de usuario y
  mensajes de commit (Conventional Commits con scope) en **castellano**.
  Verificable por inspección de commits y ficheros del intent.

## SLI/SLO del gate (informal, coste 0 €)

No hay SLO formal con burn-rate (de pago). El SLI informal del gate es:

- **Reproducibilidad**: mismo commit → mismo veredicto (soportado por R1).
- **Determinismo**: ausencia de flapping (soportado por R2; un rojo intermitente
  se arregla en el test, no bajando el piso).
- **Cobertura de rutas**: 100 % de las rutas hacia `main` (PR + push) aplican el
  mismo conjunto de controles bloqueantes (soportado por O1/O2 y la paridad de
  security-design).

## Mapeo AWS→gratuito (herramientas de observabilidad asumidas por el conocimiento del stage)

| Herramienta asumida | Equivalente gratuito | Estado |
|---------------------|----------------------|--------|
| CloudWatch dashboards/metrics | log de GitHub Actions (pasos con nombre) + `fly logs` + `/health` | Aplica (pull) |
| CloudWatch Alarms / SNS / PagerDuty | gate `verify` bloqueante + `smoke-test` + notificación de Actions (single-maintainer) | Aplica (parcial) |
| X-Ray / tracing distribuido | correlación por log estructurado + `task_id` | Diferido (de pago NO-APLICA) |
| Anomaly Detection (ML) | barreras deterministas (allowlist con caducidad, piso, pins) | Sustituido (ML NO-APLICA) |
| Cost Explorer / Trusted Advisor | documentación de minutos + mandato coste 0 € | Sustituido (O5) |

## Trazabilidad

- NFR-OBS.1 → O1; NFR-OBS.2 → O2; NFR-OBS.3 → O3; NFR-OBS.4 → O4;
  NFR6.1 → O5; NFR3.1 → O6; NFR6.2 → O7.

## Sources

- `../nfr-requirements/observability-requirements.md` (NFR-OBS.1–4, NFR6.1, NFR3.1, NFR6.2).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (mapeo AWS→gratuito, SLI informal).

## Assumptions & Open Questions

- None.
