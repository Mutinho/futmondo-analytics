# Team Assessment — F3 Mercado (app nativa iOS)

> Contexto de entrega: el "equipo" es el **flujo AI-DLC** operado por un único
> propietario, con un **agente conductor** que adopta personas de dominio y
> delega etapas puntuales a sub-agentes. No hay un equipo humano multi-persona;
> este assessment lo refleja con honestidad y dimensiona la entrega en
> consecuencia.

## Sources

- `.../ideation/scope-definition/scope-document.md` y `intent-backlog.md` —
  alcance y MoSCoW.
- `.../ideation/feasibility/feasibility-assessment.md` — viabilidad y esfuerzo.

## Composición efectiva

- **Propietario / único stakeholder humano**: decide en cada gate, valida en
  dispositivo (iPhone 13 Pro con `xtool`).
- **Conductor AI-DLC**: ejecuta las etapas adoptando la persona de dominio
  (product, architect, developer…), delega revisiones y unidades a sub-agentes.
- **Sub-agentes delegados**: developer (code-generation), reviewers (product-lead,
  architecture-reviewer) según lo pida cada etapa.

## Capacidad vs demanda

- La feature es de **tamaño baja-media** (pantalla existente, endpoints en
  producción, base F1/F2). La capacidad del flujo AI-DLC es suficiente; el cuello
  de botella real es la **validación en dispositivo** (sólo allí afloran errores
  arm-only).

## Riesgos de entrega

- Igual que F1/F2: rondas de ida/vuelta por errores arm-only que no se ven en
  WSL. Mitigación: rigor anti-hueco-WSL antes de pedir reinstalar en dispositivo.

## Assumptions & Open Questions

None.
