# Wireframes — F3 Mercado (app nativa iOS)

> Wireframes de baja fidelidad (esquemáticos) de la pantalla de Mercado nativa.
> El estilo final es el **tema oscuro/neón** y los componentes del `DesignSystem`
> de F1/F2; aquí se fija la **estructura y jerarquía**, no el pixel. Fuente de
> verdad del contenido: la vista Angular de Mercado.

## Sources

- `.../ideation/intent-capture/intent-statement.md` — resultado esperado.
- `.../ideation/scope-definition/scope-document.md` y `intent-backlog.md` —
  elementos dentro de alcance (banner, cards, orden, puja/cancelar, Sofascore).
- `angular-app/src/app/features/market/market.component.html` — estructura real
  de banner y cards.

## W1 — Pantalla de Mercado (pestaña 2)

```text
┌──────────────────────────────────────────┐
│  Mercado                           (icon)  │  ← page header (DesignSystem)
│  Jugadores del computer disponibles…       │
├──────────────────────────────────────────┤
│  [Presupuesto] [En pujas] [Balance]        │  ← banner user_info (chips/tiles)
│  [Puja máxima] [Disponible]                │     Balance/Disponible con color
├──────────────────────────────────────────┤
│  N jugadores disponibles     [Orden ▼]     │  ← contador + selector de orden
│   orden: Valor · Tendencia · Sofascore ·   │     (descendente, 7 campos:
│   %Titular · Sugerida · Puntos · Media     │      value, change, sofascore_rating,
│                                            │      starter_pct, suggested_bid,
│                                            │      points, average)
├──────────────────────────────────────────┤
│  ┌────────────────────────────────────┐   │
│  │ (avatar)  Nombre jugador        ⭐  │   │  ← NeonGlassCard (favorito opc.)
│  │           (logo) Equipo             │   │
│  │           [Sofascore] [% Titular]   │   │  ← badges
│  │                        [POS] [POS2] │   │  ← position chips
│  │  VALOR      TENDENCIA   PRECIO MERC. │   │  ← grid stats (fila 1)
│  │             ↗/↘ ±valor               │   │     (flecha + signo, no sólo color)
│  │  SUGERIDA   PUNTOS      MEDIA        │   │  ← grid stats (fila 2)
│  │  ┌──────────────────────────────┐   │   │
│  │  │   PUJAR  {puja sugerida}      │   │   │  ← acción (si no hay puja)
│  │  └──────────────────────────────┘   │   │
│  └────────────────────────────────────┘   │
│  ┌────────────────────────────────────┐   │
│  │ … (card con puja activa) …          │   │
│  │  🏷 Puja activa: {current_bid}  [✕] │   │  ← fila puja activa + cancelar
│  └────────────────────────────────────┘   │
│                                      (↑)   │  ← scroll-to-top
├──────────────────────────────────────────┤
│   [ Presupuesto ]        [ • Mercado ]     │  ← TabView 2 pestañas (Liquid Glass)
└──────────────────────────────────────────┘
```

Estados: **cargando** (spinner + "Cargando mercado…"), **error** (mensaje +
reintento), **vacío** ("No hay jugadores del computer…"), **con datos** (lista).

## W2 — Diálogo de puja (sheet)

```text
┌───────────────────────────────┐
│  🔨 Pujar por {Nombre}         │
├───────────────────────────────┤
│  Valor de mercado (mín): X     │
│  Puja máxima permitida:  Y     │
│                               │
│  Cantidad a pujar: [ € ____ ]  │  ← default = puja sugerida
│  (validación inline:            │
│   · vacía o ≤ 0 → "debe ser     │
│     mayor que 0"                │
│   · fuera de [mín, máx] →       │
│     mensaje con el límite)      │
├───────────────────────────────┤
│         [Cancelar]  [Pujar]    │
└───────────────────────────────┘
```

## W3 — Confirmación de cancelación (sheet/alert)

```text
┌───────────────────────────────┐
│  ❌ Cancelar Puja              │
│  ¿Cancelar puja de {X} por     │
│   {Nombre}?                    │
│        [No]  [Cancelar puja]   │
└───────────────────────────────┘
```

## W4 — Detalle Sofascore (sheet)

```text
┌───────────────────────────────┐
│  ⚽ {Nombre}                   │
│        (rating grande)         │  ← rating hero + torneo/temporada
│  [Partidos][Titular][%Tit.]…   │  ← grid de stats (carga async)
│  (estados: cargando / error)   │
│                      [Cerrar]  │
└───────────────────────────────┘
```

## Notas de accesibilidad (WCAG / HIG)

- Contraste del texto sobre el fondo oscuro/neón conforme al `DesignSystem` de
  F1/F2 (ya validado); los colores money-positive/negative no son el único
  portador de significado (se acompañan de signo ▲/▼ y etiqueta).
- Botones de acción con área táctil suficiente y etiqueta accesible ("Pujar por
  {importe}", "Cancelar puja").
- El selector de orden y los badges son operables con VoiceOver.

## Assumptions & Open Questions

None.
