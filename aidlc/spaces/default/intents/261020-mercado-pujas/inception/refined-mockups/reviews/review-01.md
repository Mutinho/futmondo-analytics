### Review — Refined Mockups (F3 Mercado)

**Reviewer:** aidlc-product-lead-agent
**Review artifact:** mockups.md
**Class:** advisory
**Iteration:** 1

**Verdict:** READY

### Resumen

Los mockups cubren el alcance de F3 a nivel de Inception (pantalla principal con
estados loading/error/vacío/datos, sheet de puja con validación, confirmación de
cancelación destructiva, sheet Sofascore con carga aislada), reutilizan el
DesignSystem de F1/F2 sin dependencias de pago, y distinguen correctamente card
sin puja (botón "PUJAR") vs con puja activa (fila cancelar). Cero Critical, cero
Major.

### Findings (Minor, aplicados)

- Minor — M1: nombrado el orden por defecto descendente por `value` y el estado
  preseleccionado del selector. **Aplicado.**
- Minor — M2: anotado el tope efectivo `available_for_bids` (divergencia
  intencionada Q1=A frente a `max_bid` del Angular) y el rango de validación.
  **Aplicado.**
- Minor — M2/M3: añadida nota remitiendo al patrón de desenlaces de
  `interaction-spec.md` (éxito recarga; rechazo/error no). **Aplicado.**

Implementable sin volver a preguntar.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| - | - | - | No findings | No action required | Resolved |
