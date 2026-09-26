# Observability Requirements — Intent 4 (gate CI/CD hardening)

La observabilidad relevante es la **de la señal del gate** (¿qué ve el equipo
cuando el gate corre?), adaptada al stack real (GitHub Actions + Fly.io) y al
mandato de coste 0 €. No se introduce tracing distribuido, SLO formales con
burn-rate ni anomaly detection ML (exigirían servicios de pago); se documenta la
alternativa gratuita en su lugar.

## Requisitos

Esquema de IDs: la observabilidad de la señal del gate no tiene un NFR de
inception propio; se ancla en los FR que la originan (FR11/FR12/FR14/FR16) bajo
un slot dedicado **NFR-OBS** para evitar colisión con el slot de inception NFR6
(idioma). Los requisitos que heredan directamente de un NFR de inception
conservan su número (NFR3, NFR6).

| ID | Requisito | Criterio pass-fail | Origen (inception) |
|----|-----------|--------------------|--------------------|
| NFR-OBS.1 | Señal de cobertura backend visible en ambos gates | La cobertura backend con piso se reporta y bloquea tanto en `ci.yml` (PR) como en el job `verify` (push), de modo que el estado de cobertura sea observable en cualquier ruta hacia `main`. | FR11, FR14.1 |
| NFR-OBS.2 | Estado de audits/lint observable como paso propio | Cada audit (`pip-audit`/`npm audit`) y el lint (`ruff check`) aparecen como pasos identificables en el log del workflow, con su resultado (pass/fail) visible; no se ocultan tras `continue-on-error` una vez promovidos. | FR12, FR14.2 |
| NFR-OBS.3 | Trazabilidad de excepciones de seguridad | La allowlist versionada (findings sin fix) es observable en git: qué se aceptó, por qué y hasta cuándo (fecha de caducidad). | FR12.5 |
| NFR-OBS.4 | Verificación de release intacta | El smoke test contra `/health` (5 reintentos, HTTP 200) sigue siendo la señal de éxito del release; `fly logs` y el healthcheck son las herramientas de observabilidad de runtime gratuitas ya existentes. | FR14.3 |
| NFR6.1 | Consumo de free tier documentado | El consumo de minutos de GitHub Actions (y su margen frente al allowance gratuito) queda documentado como observabilidad de coste. | FR16 |
| NFR3.1 | No reformateo brownfield preserva la señal de revisión | Ningún endurecimiento ejecuta `ruff format`/Prettier en masa sobre ficheros heredados; solo ficheros nuevos o cambios quirúrgicos. Criterio: el diff de cada commit `chore(ci)` no contiene reflow ajeno al cambio, de modo que la señal de la reviewer (que solo corre `ruff check`) se mantiene estable. | NFR3 |
| NFR6.2 | Idioma de los artefactos y commits | Identificadores/docstrings/comentarios en inglés; texto de usuario y mensajes de commit (Conventional Commits con scope) en castellano. Verificable por inspección de los commits y ficheros del intent. | NFR6 |

## No aplica a coste 0 € (documentado, no implementado)

- **Tracing distribuido, SLO formales con burn-rate alerting, dashboards
  dedicados, anomaly detection**: exigen servicios de pago o infraestructura
  adicional. Fuera de alcance por el mandato de coste 0 €. La alternativa
  gratuita es el propio log de GitHub Actions, `fly logs` y el healthcheck
  `/health` ya operativos.

## Sources

- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/requirements-analysis/requirements.md` (FR11, FR12, FR14, FR16).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (adaptación Fly.io/GitHub Actions a coste 0 €).

## Assumptions & Open Questions

- None.
