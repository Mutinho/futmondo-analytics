# Reliability Requirements — Intent 4 (gate CI/CD hardening)

La fiabilidad relevante aquí es la **del propio gate de CI/CD como red de
seguridad**: debe ser reproducible (mismo veredicto ante el mismo commit),
determinista (sin flapping), y con rollback quirúrgico. La disponibilidad de la
aplicación en runtime (SLA/SLO de la app, tolerancia a fallos, recovery de datos)
**no cambia** con este intent.

## Requisitos

Esquema de IDs: cada requisito hereda del NFR de inception del que deriva. La
reproducibilidad/no-flapping del gate deriva de **NFR5**; el rollback quirúrgico
deriva de **NFR2** (aislamiento por commit); la intactitud de la cadena de
release y el no-relajar-garantías se anclan en los FR que los originan
(FR14/FR11/FR12) bajo un slot de fiabilidad dedicado **NFR-REL** para evitar
colisión con los slots de inception.

| ID | Requisito | Criterio pass-fail | Origen (inception) |
|----|-----------|--------------------|--------------------|
| NFR5.1 | Gate reproducible | El veredicto del gate no debe depender de qué resuelva el gestor de paquetes ese día: `pip-audit` audita el entorno instalado/resuelto (no rangos), y el tooling del gate (`ruff`, `pip-audit`, `vitest`, gitleaks) está a versión exacta. Dos ejecuciones sobre el mismo commit dan el mismo resultado. | NFR5, FR12.4, FR13 |
| NFR5.2 | Sin flapping en el piso de cobertura | El piso `--cov-fail-under` se fija al valor medido exacto sobre la suite estabilizada. Un rojo intermitente por no-determinismo se resuelve arreglando el test no-determinista, NUNCA bajando el piso ni añadiendo margen de holgura. | NFR5, FR11.2, FR11.3 |
| NFR2.1 | Rollback quirúrgico | Cada endurecimiento (piso, promoción advisory→bloqueante, unificación/pin de versión) va en su propio commit `chore(ci)` aislado con el trinquete fijado, de modo que revertir uno no arrastre los demás. | NFR2 |
| NFR-REL.1 | Cadena de release intacta | El endurecimiento refuerza el CONTENIDO del job `verify`, sin reordenar la cadena `needs:` (`verify` → `deploy-backend` → `deploy-frontend` → `smoke-test`); el smoke test `/health` (5 reintentos, HTTP 200) sigue siendo la verificación de release. | FR14.3 |
| NFR-REL.2 | El gate no relaja garantías | Ningún endurecimiento puede bajar un umbral/piso existente ni dejar `continue-on-error` permanente en un check promovido; el ratchet (backend y frontend) solo sube. | FR11.3, FR12.5 |

## Runtime de la app — N/A (con justificación)

- **SLA/SLO de disponibilidad de la app, tolerancia a fallos del servicio,
  backup/recovery de Neon, degradación elegante**: N/A. El intent no toca el
  runtime; estas garantías son las de la línea base en producción y no cambian.

## Sources

- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/requirements-analysis/requirements.md` (FR11–FR14, NFR2, NFR5).
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/team-practices.md` (Deployment, Q6).

## Assumptions & Open Questions

- El valor numérico del piso de cobertura backend (NFR5.2) se mide en ci-pipeline; la política (valor exacto, sin margen, solo trinquete) ya está afirmada.
