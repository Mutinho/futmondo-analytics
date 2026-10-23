# Competitive Analysis — F3 Mercado (app nativa iOS)

> Alcance honesto: F3 es una **feature interna** (brownfield) que **reproduce en
> nativo una pantalla que ya existe** en nuestra propia PWA Angular, para un
> único usuario/propietario. No hay un mercado comercial que conquistar ni
> competidores a los que arrebatar cuota. Este análisis es, por tanto,
> deliberadamente acotado y se centra en las **alternativas reales** que tiene el
> usuario para hacer la misma tarea hoy.

## Sources

- `aidlc/spaces/default/intents/261020-mercado-pujas/ideation/intent-capture/intent-statement.md`
  — intent, resultado esperado, alcance (lectura + escritura + detalle Sofascore).
- `README.md` — descripción del producto (PWA instalable en iPhone) y de la
  sección Mercado.
- `angular-app/src/app/features/market/` — la implementación Angular existente,
  que es la referencia funcional directa.

## Alternativas actuales del usuario (para la misma tarea)

| Alternativa | Qué ofrece hoy | Fricción frente a F3 |
|---|---|---|
| **PWA Angular (producto propio)** en Safari iPhone | Mercado completo: banner, lista, pujar, cancelar, detalle Sofascore | Experiencia de navegador/PWA; el objetivo de F3 es la **misma función en nativo**, con el tema oscuro/neón y la fluidez del cliente iOS |
| **App oficial de Futmondo** | Gestión del juego, incluido su propio mercado | No incluye nuestra **puja sugerida basada en historial** ni el **rating Sofascore / % titular** integrados, que son el valor diferencial de nuestro producto |
| **Web de Futmondo en el navegador** | Mercado del juego | Igual que la app oficial: sin nuestras métricas analíticas |

## Lectura competitiva

- El **diferencial** de nuestro producto (y por tanto de esta pantalla) no es el
  acto de pujar en sí, sino **con qué información** se decide la puja: puja
  sugerida, Sofascore, % de titularidad, tendencia. F3 debe preservar ese
  diferencial 1:1 con la PWA (confirmado Q2=A: card con todos los campos).
- F3 no compite con Futmondo; **lo complementa**: el usuario sigue jugando en
  Futmondo, y nuestra app le da la capa analítica. La escritura (pujar/cancelar)
  se propaga a Futmondo, de modo que nuestra app actúa como **cliente
  enriquecido**, no como reemplazo.

## Assumptions & Open Questions

None.
