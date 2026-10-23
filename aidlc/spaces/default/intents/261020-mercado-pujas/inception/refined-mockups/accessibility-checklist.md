# Accessibility Checklist — F3 Mercado (app nativa iOS)

> WCAG / Apple HIG aplicados a la pantalla de Mercado. Hereda la base de contraste
> ya validada en F1/F2.

## Sources

- `.../inception/refined-mockups/mockups.md` e `interaction-spec.md`.
- `.kiro/knowledge/aidlc-design-agent/accessibility-wcag.md`.

## Checklist

- [ ] **Contraste**: texto y badges sobre el fondo oscuro/neón cumplen AA
  (heredado del `DesignSystem` de F1/F2).
- [ ] **No sólo color**: la tendencia usa flecha ↗/↘ + signo además del color;
  Balance/Disponible muestran el signo numérico además del color.
- [ ] **Etiquetas accesibles**: botones de acción con `accessibilityLabel`
  explícito ("Pujar por {importe}", "Cancelar puja de {jugador}", "Ver detalle
  Sofascore de {jugador}").
- [ ] **VoiceOver**: cada card expone un resumen legible (nombre, equipo, valor,
  puja sugerida); el selector de orden y los badges son operables.
- [ ] **Área táctil**: botones ≥ 44×44 pt (HIG).
- [ ] **Estados comunicados**: loading/error/vacío anunciados (no sólo visuales);
  los avisos de resultado de puja/cancelación son perceptibles por VoiceOver.
- [ ] **Teclado numérico**: el campo de importe usa teclado numérico y respeta
  Dynamic Type.
- [ ] **Foco**: al abrir un sheet, el foco de VoiceOver entra en su título.

> Verificación final en dispositivo (iPhone 13 Pro) por el propietario, junto con
> la validación visual.

## Assumptions & Open Questions

None.
