# Refined Mockups — Preguntas y Resumen (F3 Mercado)

> Modo **Guíame**. Mockups refinados con mapeo al DesignSystem de F1/F2. Confirmo
> una decisión de interacción.

---

## Q1 — Pull-to-refresh

- **A.** Incluir **pull-to-refresh** en la lista de Mercado (coherente con F2) para
  recargar manualmente, además de la recarga automática tras pujar/cancelar y al
  cambiar de campeonato. ← **recomendada**.
- **B.** Sin pull-to-refresh; sólo recarga automática.
- **X.** Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de Refined Mockups para F3 = Mercado:

- **M1 Pantalla**: AuthenticatedBackground + page header + banner (5 métricas con
  moneyPositive/Negative) + barra de orden + LazyVStack de NeonGlassCard (header,
  grid de métricas, acción PUJAR / fila "Puja activa"+cancelar, favorito);
  estados LoadingState/ErrorState/EmptyState de F2.
- **M2 Sheet de puja**: tiles de límite, TextInputField numérico (default
  sugerida), validación inline, Pujar/Cancelar.
- **M3 Cancelación**: confirmationDialog/alert nativo.
- **M4 Sheet Sofascore**: rating hero + grid, estados cargando/error/datos.
- **Interaction spec**: `bidding` deshabilita botones; recarga sólo en éxito;
  avisos en castellano; (Could) háptico y transición de card.
- **Design system mapping**: reutiliza NeonGlassCard, PrimaryButton,
  GlassIconButton, TextInputField, Chips, DSColor/DSFont/DSSpacing, MoneyFormatter,
  estados de F2; sheets/alert con HIG.
- **Accesibilidad**: contraste heredado, no-sólo-color, etiquetas, VoiceOver, 44pt.
- **Reviewer advisory** (product-lead) sobre `mockups`: pendiente (ahora).
- **Siguiente etapa**: Domain Design.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
