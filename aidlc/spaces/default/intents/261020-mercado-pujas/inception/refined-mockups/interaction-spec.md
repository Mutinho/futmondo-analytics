# Interaction Spec — F3 Mercado (app nativa iOS)

## Sources

- `.../inception/refined-mockups/mockups.md`.
- `.../inception/user-stories/stories.md` (US1–US7).
- `angular-app/src/app/features/market/market.component.ts` (flujos).

## Interacciones

| Gesto / evento | Resultado |
|---|---|
| Seleccionar pestaña "Mercado" | Carga `GET /market/today` del campeonato activo; muestra estado correspondiente |
| Cambiar campeonato activo | Recarga el mercado |
| Elegir campo de orden | Reordena descendente in-memory, sin recarga; nulos al final |
| Pulsar "PUJAR" | Abre sheet de puja (default = sugerida) |
| Editar importe en el sheet | Validación inline en vivo; habilita/deshabilita "Pujar" |
| Confirmar puja | `POST /market/bid`; durante la llamada, botones deshabilitados; al volver, aviso (éxito/rechazo/error) y, si éxito, recarga |
| Pulsar cancelar en puja activa | Abre confirmación |
| Confirmar cancelación | `POST /market/cancelbid`; mismo patrón de aviso + recarga en éxito |
| Tocar badge Sofascore | Abre sheet de detalle; carga async aislada |
| Pull-to-refresh (opcional, coherente con F2) | Recarga el mercado |

## Reglas de estado

- **`bidding` (escritura en curso)**: deshabilita todos los botones de puja y
  cancelar para evitar doble envío; se limpia al terminar (éxito o fallo).
- **Recarga sólo en éxito**: un rechazo de backend o un error de red **no**
  recargan (evita perder el contexto del aviso).
- **Avisos**: estilo snackbar/toast coherente con el DesignSystem; mensajes en
  castellano.

## Microinteracciones (Could, si da tiempo)

- Háptico ligero al confirmar puja/cancelación con éxito (coherente con F2).
- Transición suave de la card al pasar de "PUJAR" a "Puja activa" tras pujar.

## Assumptions & Open Questions

None.
