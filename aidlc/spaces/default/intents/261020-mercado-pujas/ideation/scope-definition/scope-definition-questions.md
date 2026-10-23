# Scope Definition — Preguntas y Resumen (F3 Mercado)

> Modo **Guíame**. El alcance ya quedó decidido en Intent Capture (Q1–Q4 = A);
> aquí lo formalizo en documento + backlog MoSCoW y confirmo la priorización.

---

## Q1 — Priorización del detalle Sofascore

El detalle Sofascore está **dentro de alcance** (Q3=A). En el backlog lo he
marcado **Should (S1)** —no Must— por ser el elemento de menor acoplamiento, que
podría diferirse sin romper el núcleo del Mercado si hiciera falta recortar.

- **A.** Mantener Sofascore como **Should (S1)**: se implementa en F3, pero es lo
  primero que se recortaría ante presión de tiempo. ← **recomendada**.
- **B.** Elevarlo a **Must**: Sofascore es imprescindible en F3 al mismo nivel que
  pujar/cancelar.
- **X.** Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de Scope Definition para F3 = Mercado:

- **Navegación**: `RootTabView` de 1 → **2 pestañas** (Presupuesto + Mercado).
- **Must**: 2ª pestaña (M1), carga (M2), banner (M3), cards 1:1 (M4), orden
  descendente (M5), **pujar** (M6), **cancelar** (M7).
- **Should**: detalle Sofascore como sheet (S1), marca de favorito (S2).
- **Could**: microinteracciones/hápticos coherentes con F2 (C1).
- **Won't (este intent)**: tabla (W1), Calculadora/Finanzas = F4 (W2), pestañas
  extra (W3), cambios de backend (W4), distribución + asset catalog (W5).
- **Siguiente etapa**: Team Formation.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
