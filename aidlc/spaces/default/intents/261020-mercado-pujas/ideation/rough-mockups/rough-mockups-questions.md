# Rough Mockups — Preguntas y Resumen (F3 Mercado)

> Modo **Guíame**. Wireframes de baja fidelidad fieles a la vista Angular, con el
> tema oscuro/neón de F1/F2. Confirmo estructura y una decisión de presentación.

---

## Q1 — Presentación de los diálogos de escritura y del detalle Sofascore

- **A.** Todos como **sheets** nativas (puja, confirmación de cancelación y
  detalle Sofascore), coherente con iOS/HIG y con el patrón de F2. ←
  **recomendada**.
- **B.** Confirmación de cancelación como **alert** nativo (más ligero) y el
  resto como sheets.
- **X.** Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de Rough Mockups para F3 = Mercado:

- **W1 Pantalla Mercado**: page header + banner (Presupuesto/En pujas/Balance/
  Puja máxima/Disponible) + contador + selector de orden + lista de
  `NeonGlassCard` (avatar, nombre, equipo, badges Sofascore/%titular, chips de
  posición, grid de stats, acción PUJAR o fila "Puja activa" + cancelar) +
  scroll-to-top; dentro del `TabView` de 2 pestañas. Estados cargando/error/
  vacío/datos.
- **W2 Puja**: sheet con importe (default sugerida, validación mín/máx).
- **W3 Cancelación**: confirmación.
- **W4 Sofascore**: sheet con rating + grid de stats (carga async, loading/error).
- **User flow**: ver → ordenar → pujar (con señal aceptada/rechazada/error +
  recarga) / cancelar; botones deshabilitados durante la escritura.
- **Accesibilidad**: contraste del DesignSystem, significado no sólo por color,
  etiquetas accesibles, VoiceOver.
- **Reviewer advisory** (product-lead) sobre `wireframes`: pendiente (se corre
  ahora).
- **Siguiente etapa**: Approval & Handoff (cierre de Ideación).

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
