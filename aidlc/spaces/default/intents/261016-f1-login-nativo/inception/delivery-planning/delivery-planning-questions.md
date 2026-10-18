# Delivery Planning — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1 — ¿El plan de bolts, la secuencia y las dependencias son correctos?

- A. **Correctos** — proceder a construcción (functional design del primer bolt) (recomendado).
- B. Correctos con un ajuste (p. ej. sub-batchear Bolt 3 ya, o cambiar la autonomía).
- C. Replantear (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar delivery-planning (y la fase de inception), confirma:

- **3 bolts (camino lineal, squash-merge)**: Bolt 1 `backend-refresh-transport` (service, primero
  por riesgo de regresión + base del transporte) → Bolt 2 `ios-network-client` (library) → Bolt 3
  `ios-native-auth` (ui, el de mayor alcance; sub-batching opcional en construcción).
- **Skeleton**: OFF (sistema ya en producción).
- **Secuenciación risk-first**: backend primero y aislado con gate + tests de ambos canales (R-01);
  Keychain/refresh en Bolt 3 con diseño por capas (R-02/R-03).
- **Dependencias externas**: backend reutilizado, cadena `xtool` (spike F0), Apple ID gratuito,
  gate de CI, iPhone 13 Pro; sin coste recurrente nuevo.
- **Equipo**: ejecutor único.

¿Está todo correcto?

[Answer]: Looks correct
