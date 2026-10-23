# Market Trends — F3 Mercado (app nativa iOS)

> Acotado a lo que es **relevante y verificable** para esta feature interna. No
> se presentan cifras de mercado especulativas (la fase de ideación prohíbe
> presentar especulación como hecho); se recogen tendencias de plataforma que
> condicionan decisiones de diseño/implementación.

## Sources

- `aidlc/spaces/default/intents/261020-mercado-pujas/ideation/intent-capture/intent-statement.md`
  — alcance nativo (SwiftUI, 2ª pestaña del `TabView`).
- `aidlc/spaces/default/memory/project.md` / `team.md` — mandatos durables (coste
  0 €, SDK de Apple, tema Angular como fuente de verdad) y aprendizajes de F1/F2.
- F1/F2 cerrados: `DesignSystem` oscuro/neón y `RootTabView` ya en producción en
  `ios/`.

## Tendencias relevantes (hipótesis/observaciones)

- [observación] **Preferencia por app nativa en iPhone** para uso recurrente: el
  usuario ya pidió llevar a nativo primero el Presupuesto (F2) y ahora el
  Mercado, lo que confirma la dirección de portar sección a sección las
  pantallas de mayor uso. (Fuente: historial de intents F1→F2→F3.)
- [observación] **Liquid Glass / iOS 26** como lenguaje visual vigente del
  cliente nativo: `Package.swift` ya fija `.iOS("26.0")` y el `RootTabView` usa
  Liquid Glass. F3 se alinea con ese lenguaje sin introducir dependencias.
- [hipótesis] El valor de uso se concentra en **decidir pujas con datos**
  (Sofascore, puja sugerida); la tendencia de producto es reforzar esa capa
  analítica, no replicar la mecánica de juego de Futmondo.

## Implicaciones para F3

- Mantener el tema oscuro/neón y los componentes de F1/F2 (no reinventar UI).
- La escritura nativa debe sentirse tan fiable como la web: confirmación,
  validación y señal clara de resultado.

## Assumptions & Open Questions

None.
