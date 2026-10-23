# Wireframes (low-fidelity) — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (rough-mockups). Idioma: castellano; tokens técnicos verbatim en inglés.
> ASCII de baja fidelidad. La fidelidad visual fina (tema Angular Material 3) se detalla en refined-mockups.

## Pantalla 1 — Presupuesto (estado normal)

```
┌─────────────────────────────────────┐
│  Liga Pepe ▾            [ ⇅ Ordenar ]│  ← navigation bar (top): título = campeonato activo (menú ▾) + menú de orden
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ Equipo Javi                     │ │  ← fila/card por equipo
│ │ SALDO        12,4M  (money-pos) │ │
│ │ RENDIMIENTO  +3,1M  (money-pos) │ │
│ │ PUJA MÁX     8,0M     PREMIOS 2M│ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ Equipo Ana                      │ │
│ │ SALDO       -1,2M  (money-neg)  │ │
│ │ RENDIMIENTO -0,5M  (money-neg)  │ │
│ │ PUJA MÁX     5,5M     PREMIOS  - │ │
│ └─────────────────────────────────┘ │
│            … (scroll) …              │
├─────────────────────────────────────┤
│   [ 💰 Presupuesto ]                 │  ← TabView (bottom), 1 sola pestaña, Liquid Glass iOS 26
└─────────────────────────────────────┘
```

Nota accesibilidad: cada fila es un elemento VoiceOver con label compuesto ("Equipo Javi, saldo 12,4 millones positivo, rendimiento +3,1 millones…"). Dynamic Type escala los valores. El color money-positive/negative NUNCA es el único portador de significado (se acompaña de signo).

## Pantalla 1b — Selector de campeonato desplegado (menú en navigation bar)

```
┌─────────────────────────────────────┐
│  Liga Pepe ▾                         │
│  ┌───────────────────────────┐      │  ← Menu nativo desplegado desde el título
│  │ ✓ Liga Pepe               │      │
│  │   Liga Trabajo            │      │
│  │   Liga Family             │      │
│  └───────────────────────────┘      │
│   (al elegir: recarga Presupuesto    │
│    + persiste en UserDefaults)       │
└─────────────────────────────────────┘
```

## Pantalla 1c — Estados de carga y error

```
  Cargando:                 Error:
  ┌──────────────┐          ┌──────────────────────────┐
  │   (spinner)  │          │  No se pudo cargar el     │
  │  Cargando…   │          │  presupuesto. [Reintentar]│
  └──────────────┘          └──────────────────────────┘
```

## Orden (menú de ordenación)

Opciones: Saldo · Rendimiento · Puja Máxima · Valor Plantilla · Gastado · Ingresado (mismas claves que la web). Selección actual marcada con ✓.

## Assumptions & Open Questions

None.
