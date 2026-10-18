# Cost Analysis — F1: Login nativo end-to-end

> Fase: operación (feedback-optimization). Idioma: castellano; tokens técnicos verbatim en inglés.
> Sin AWS Cost Explorer / Trusted Advisor (otro stack): el análisis de coste es la **verificación
> del mandato de coste 0 €** sobre el stack real (tiers gratuitos), más la excepción acotada de
> publicación nativa.

## Coste recurrente de F1

| Recurso | Tier | Coste recurrente |
|---------|------|------------------|
| Fly.io (`futmondo-api` + `futmondo-app`, región `cdg`) | free allowance | 0 € |
| Neon PostgreSQL (Frankfurt) | free | 0 € |
| GitHub Actions (CI + deploy) | free | 0 € |
| Dependencias del cliente iOS | solo SDK de Apple (sin librerías de pago) | 0 € |
| Dependencias backend (D-01) | aditivo, stdlib/FastAPI existente (sin deps nuevas) | 0 € |
| Firma de la app iOS | Apple free-signing (~7 días) | 0 € |

**Coste recurrente total de F1: 0 €.** F1 no introduce ningún servicio ni dependencia con gasto
recurrente (mandato durable cumplido).

## Excepción acotada conocida (NO incurrida en F1)

- **Publicación en App Store** (Apple Developer Program ~99 €/año): excepción **aceptada y
  acotada** al mandato de coste 0 €, exclusivamente para habilitar la distribución nativa. En F1
  **no se incurre** porque la distribución es por firma gratuita (B-09 diferido). Queda documentada
  como coste recurrente **futuro** si se decide publicar.

## Oportunidades de optimización

- Ninguna optimización de coste pendiente: F1 ya está en el mínimo (tiers gratuitos). No hay
  sobre-provisión que recortar (entorno único, sin recursos ociosos de pago).
- Recomendación: mantener el guardarraíl de "no introducir dependencias/servicios de pago" en
  futuros intents (regla durable ya afirmada).

## NO-APLICA (otro stack)

| AWS (stage) | Estado |
|---|---|
| Cost Explorer / Trusted Advisor | NO-APLICA; sustituido por verificación del mandato coste 0 € sobre tiers gratuitos |

## Sources

- [consumes] deployment-log.md; requirements.md (NFR-2 coste 0 €).
- [memory] team.md `## Deployment` (restricción dura coste 0 € + excepción acotada Q1=B); project.md
  (coste 0 € + excepción de publicación nativa); aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
