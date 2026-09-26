# SLO Config — Intent 4 (gate CI/CD hardening)

> Fase Operation. Conocimiento SLO/SLI con burn-rate y error budget **adaptado a
> coste 0 €**: no hay motor de SLO ni burn-rate alerting (de pago). Se define un
> **SLI informal** observable con herramientas gratuitas y se marca el **SLO
> formal con ventana/burn-rate como NO-APLICA/diferido** (Q2=A, regla afirmada
> learned 2026-09-16).

## SLI informal (observable, coste 0 €)

| SLI | Definición | Medición (gratuita) |
|-----|-----------|---------------------|
| Disponibilidad de release | `/health` responde 200 tras cada deploy | job `smoke-test` (5 reintentos, HTTP 200) |
| Reproducibilidad del gate | mismo commit → mismo veredicto | comparar ejecuciones del gate en el log de Actions |
| No-flapping del gate | 0 rojos intermitentes por no-determinismo | inspección de rojos recurrentes; un flake se arregla en el test |
| Cobertura de rutas hacia `main` | 100 % (PR + push aplican el mismo gate bloqueante) | presencia de los pasos en `ci.yml` y `verify` |

## SLO formal — NO-APLICA (documentado)

- **SLO con % objetivo + ventana de 30 días + error budget + burn-rate
  alerting**: **NO-APLICA** en este intent y este stack a coste 0 €. Exige un
  motor de SLO (CloudWatch/Grafana SLO, de pago) y una métrica de disponibilidad
  continua que este stack no instrumenta.
- **Alternativa gratuita**: el SLI informal anterior + el gate bloqueante como
  barrera pre-producción (un rojo nunca llega a `main`) + el smoke test `/health`
  como verificación de release. Es la mejor aproximación sostenible sin coste.
- **Deuda diferida**: si en el futuro se adopta un plan con SLO formal, se
  cuantificarían objetivos (p. ej. disponibilidad de `/health`) con ventana y
  burn-rate; hoy queda fuera de alcance por el mandato coste 0 €.

## Nota sobre el guardrail de Operation

El guardrail de Operation pide "SLOs cuantificados con % y ventana". Aquí se
documenta explícitamente por qué NO-APLICA (coste) y qué SLI informal lo
sustituye, en vez de inventar un motor de SLO inexistente — coherente con la
regla afirmada de adaptación al stack real.

## Sources

- `../../construction/nfr-design/reliability-design.md`, `observability-design.md`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (SLI informal, SLO de pago NO-APLICA).

## Assumptions & Open Questions

- SLO formal con burn-rate queda como deuda documentada; fuera de alcance por coste 0 €.
