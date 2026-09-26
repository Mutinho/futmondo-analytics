# Anomaly Detection Config — Intent 4 (gate CI/CD hardening)

> Fase Operation. La detección de anomalías por ML (CloudWatch Anomaly Detection)
> **NO-APLICA** en este stack a coste 0 € (Q4=A). Se documenta el sustituto por
> barreras deterministas.

## Anomaly detection ML — NO-APLICA (documentado)

- **CloudWatch Anomaly Detection / bandas ML sobre métricas**: **NO-APLICA**
  (coste + requiere un motor de métricas continuo inexistente). No hay una
  métrica de latencia/error-rate instrumentada con histórico sobre la que
  entrenar una banda.

## Sustituto gratuito: barreras deterministas

En vez de detectar desviaciones por ML, el gate endurecido introduce **barreras
deterministas** que atrapan las clases de "anomalía" relevantes a coste 0 €:

| Clase de anomalía | Barrera determinista | Dónde |
|-------------------|----------------------|-------|
| Dependencia vulnerable nueva | `pip-audit` (con fix) / `npm audit` (`high`) bloqueantes | gate PR + `verify` |
| Excepción de seguridad caducada | script de expiry de la allowlist | gate PR + `verify` |
| Regresión de cobertura | piso `--cov-fail-under` (backend) + ratchet (frontend) | gate PR + `verify` |
| Veredicto no reproducible | tooling pinneado + `pip-audit` sobre entorno instalado | gate PR + `verify` |
| Secreto filtrado | gitleaks unificado `@v3` bloqueante | gate PR + `verify` |
| Release no saludable | smoke test `/health` (5 reintentos, 200) | post-deploy |

Estas barreras son **deterministas** (no probabilísticas): un umbral claro y un
veredicto binario, coherente con el mandato coste 0 € y con la afirmación de que
el gate solo endurece.

## Relación con el intent

El intent es precisamente la instalación de estas barreras deterministas
(FR11/FR12/FR17.3). No hay una "detección de anomalías" ML que configurar; el
endurecimiento del gate ES la detección determinista de las anomalías que
importan (supply-chain, cobertura, secretos, reproducibilidad).

## Sources

- `../../construction/nfr-design/security-design.md`, `reliability-design.md`, `observability-design.md`.
- `../../construction/ci-pipeline/quality-gates.md`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (anomaly ML NO-APLICA).

## Assumptions & Open Questions

- Anomaly detection ML queda como deuda documentada; fuera de alcance por coste 0 €. Las barreras deterministas cubren las clases de anomalía relevantes.
