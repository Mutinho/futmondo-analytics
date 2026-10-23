# Refined Mockups — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (refined-mockups). Idioma: castellano; tokens técnicos verbatim en inglés.
> Recoge los findings advisory pendientes de rough-mockups (métricas visibles, estado vacío, accesibilidad de estados) y de user-stories (estado vacío, diferimiento de orden, anclaje NFR4/NFR5).

## Métricas visibles en la lista (finding rough-mockups #1 resuelto)

Cada fila de equipo de Presupuesto muestra, en esta jerarquía (de las 9 de `TeamBudget`):

- **Primario (siempre visible, grande)**: `team_name`; `balance` (token money-pos/neg); `performance` (token money-pos/neg, con signo).
- **Secundario (visible, menor)**: `max_bid` (puja máxima); `prizes` (premios; "-" si 0).
- **No en la fila (diferido a detalle, follow-up)**: `team_value`, `total_spent`, `total_income`, ops (`purchases_count + sales_count`). Nota: FR1.2 pide los 9 campos "disponibles"; en F2 la **lista** muestra los 4 primarios/secundarios y el resto queda para el detalle de equipo diferido. (Decisión de densidad para iPhone; se registra como refinamiento del alcance de la lista.)

### Pantalla de detalle de equipo (diferida — placeholder de alcance)

**Fuera de alcance de F2** (follow-up): una pantalla de detalle por equipo, alcanzable al tocar una fila, alojaría las 5 métricas restantes (`team_value`, `total_spent`, `total_income`, ops) más altas/bajas (de `GET /api/v1/analytics/balances/{team_id}`). En F2 **no se construye**; se deja esta nota para que el diferimiento de FR1.2 sea explícito y no una pérdida silenciosa. El DTO de F2 sí incluye los 9 campos (para no rehacer el modelo cuando llegue el detalle).

## Pantalla 1 — Presupuesto (estado normal, refinado)

```
┌─────────────────────────────────────┐
│  Liga Pepe ▾            [ ⇅ Ordenar ]│
├─────────────────────────────────────┤
│  Equipo Javi                         │   h3 (DSFont)
│  Saldo 12,4M        Rend. +3,1M      │   money-positive / money-positive
│  Puja máx 8,0M      Premios 2,0M     │   body secundario
│ ─────────────────────────────────── │
│  Equipo Ana                          │
│  Saldo −1,2M        Rend. −0,5M      │   money-negative / money-negative
│  Puja máx 5,5M      Premios —        │
│            … (scroll) …              │
├─────────────────────────────────────┤
│   [ 💰 Presupuesto ]                 │   TabView 1-pestaña (Liquid Glass)
└─────────────────────────────────────┘
```

## Pantalla 2 — Estado vacío (finding rough-mockups #2 / user-stories #1 resuelto)

```
Campeonato sin equipos:        Usuario sin campeonatos:
┌──────────────────────┐       ┌──────────────────────────┐
│    (icono vacío)     │       │   No tienes campeonatos.  │
│ Este campeonato no   │       │ Añádelos desde Futmondo.  │
│ tiene equipos aún.   │       │ (selector deshabilitado)  │
└──────────────────────┘       └──────────────────────────┘
```
- `teams[]` vacío → mensaje de estado vacío (no error): "Este campeonato no tiene equipos aún."
- Lista de campeonatos vacía → mensaje "No tienes campeonatos" y el menú selector queda deshabilitado.

## Pantalla 3 — Carga y error (accesibilidad explícita, finding rough-mockups #3 / user-stories #3)

```
Cargando:                    Error:
┌──────────────┐             ┌──────────────────────────┐
│  (spinner)   │             │ No se pudo cargar el       │
│  Cargando…   │             │ presupuesto. [Reintentar]  │
└──────────────┘             └──────────────────────────┘
```
- VoiceOver anuncia "Cargando presupuesto" al entrar en carga; al aparecer el error, mueve el foco a [Reintentar] y lo anuncia.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/rough-mockups/wireframes.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/{requirements-analysis/requirements.md,user-stories/stories.md}`

## Assumptions & Open Questions

None.
