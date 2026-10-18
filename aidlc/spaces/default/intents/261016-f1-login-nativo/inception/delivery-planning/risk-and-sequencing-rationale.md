# Risk & Sequencing Rationale — F1: Login nativo end-to-end

> Fase: inception (delivery-planning). Idioma: castellano; tokens técnicos verbatim en inglés.

## Por qué este orden (risk-first + dependencias)

1. **Bolt 1 — `backend-refresh-transport` primero**: estabiliza el contrato de transporte del
   refresh token (D-01). Sin él, el cliente nativo no puede refrescar. Es también el bolt de mayor
   **riesgo de regresión** (toca `auth/routes.py` en producción), por eso va primero y aislado, con
   gate y tests `pytest` de ambos canales antes de seguir. Mitiga R-01 (regresión de la PWA).
2. **Bolt 2 — `ios-network-client`**: depende del contrato de Bolt 1; es la base reutilizable de
   red. Riesgo bajo (código nuevo aislado, sin UI).
3. **Bolt 3 — `ios-native-auth`**: depende de la capa de red; integra Keychain + sesión + UI.
   Riesgo medio (manejo del Keychain, R-02; divergencia de refresh, R-03), mitigado por el diseño
   por capas (ADR-3) y el dueño único del reintento (ADR-4).

## Riesgos de entrega

| Riesgo | Mitigación en la secuencia |
|--------|----------------------------|
| Regresión de la PWA (R-01) | Bolt 1 primero, aislado, con tests de ambos canales + gate de CI. |
| Keychain mal manejado (R-02) | Bolt 3; `KeychainStore` encapsulado y verificado manualmente en iPhone. |
| Divergencia de refresh (R-03) | Contrato y dueño único del reintento fijados antes de Bolt 3. |
| Fricción de firma gratuita (~7 días) | No afecta a la secuencia; validación manual puntual. |

## Sources

- [consumes] unit-of-work-dependency.md, raid-log de F1 (R-01, R-02, R-03), contract-summary.md.

## Assumptions & Open Questions

None.
