# User Flow — F3 Mercado (app nativa iOS)

## Sources

- `.../ideation/rough-mockups/wireframes.md` — pantallas W1–W4.
- `angular-app/src/app/features/market/market.component.ts` — flujos
  `confirmBid`, `cancelBid`, `openSofascoreDetail`, `loadData`.

## Flujo principal — Ver y pujar

```text
Abrir app (sesión activa F1)
      │
      ▼
TabView ──► pestaña "Mercado"
      │
      ▼
Cargar /market/today (campeonato activo)
      │
      ├─ error ──► estado error + reintento
      ├─ vacío ──► estado vacío
      ▼
Lista de cards + banner + orden
      │
      ├─ cambiar orden ──► reordena descendente (sin recarga)
      │
      ├─ tocar "PUJAR" ──► sheet de puja (W2)
      │        │
      │        ├─ importe inválido ──► error inline, botón deshabilitado
      │        ▼
      │     confirmar ──► POST /market/bid
      │        │
      │        ├─ success ──► aviso "Puja realizada" + recargar
      │        ├─ success:false ──► aviso con message del backend
      │        └─ error red ──► aviso "Error al pujar"
      │
      └─ tocar badge Sofascore ──► sheet detalle (W4, carga async)
```

## Flujo secundario — Cancelar puja activa

```text
Card con puja activa (current_bid)
      │
      ▼
tocar [✕] cancelar ──► confirmación (W3)
      │
      ├─ No ──► vuelve sin cambios
      ▼
   confirmar ──► POST /market/cancelbid (current_bid_id)
      │
      ├─ success ──► aviso "Puja cancelada" + recargar
      ├─ success:false ──► aviso con message
      └─ error red ──► aviso "Error al cancelar"
```

## Reglas de interacción

- Durante una escritura en curso, los botones de puja/cancelar se **deshabilitan**
  (patrón `bidding`), evitando doble envío.
- Tras cualquier escritura con éxito, la pantalla **recarga** el mercado para
  reflejar el nuevo estado (saldo en pujas, puja activa).
- El fallo del detalle Sofascore **no** afecta a la lista ni a la capacidad de
  pujar.

## Assumptions & Open Questions

None.
