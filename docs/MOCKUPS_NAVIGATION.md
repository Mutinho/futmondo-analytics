# Mockups de Navegación — Futmondo Angular

**Opciones de menú para la app** (6 secciones: Presupuesto, Evolución, Estadísticas, Finanzas, Clausulables, Analytics)

---

## Opción A: Tabs Superiores (Material Tab Nav Bar)

```
┌──────────────────────────────────────────────────────────────────────┐
│  🏆 FUTMONDO                                              [🔄 Sync] │
├──────────────────────────────────────────────────────────────────────┤
│ ┌──────────┬───────────┬──────────┬──────────┬───────────┬────────┐ │
│ │💰Presup. │📊Evolución│📈 Stats  │💰Finanzas│⚽Clausul. │📊Analyt│ │
│ └──────────┴───────────┴──────────┴──────────┴───────────┴────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                     CONTENIDO DE LA PESTAÑA                          │
│                                                                      │
│                                                                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Responsive (< 768px):**
```
┌────────────────────────────┐
│  🏆 FUTMONDO        [🔄]  │
├────────────────────────────┤
│ ◀ │💰│📊│📈│💰│⚽│📊│ ▶  │  ← scroll horizontal
├────────────────────────────┤
│                            │
│   CONTENIDO                │
│                            │
└────────────────────────────┘
```

**Pros:**
- Familiar (patrón más usado en dashboards)
- Todas las opciones visibles de un vistazo
- Angular Material lo soporta nativamente (`mat-tab-nav-bar`)
- Muy simple de implementar

**Contras:**
- Con 6 tabs puede quedar apretado en tablets
- En móvil necesita scroll horizontal (menos intuitivo)
- No deja espacio para sub-navegación de Analytics

---

## Opción B: Sidebar Lateral Colapsable (estilo Admin Panel)

```
┌─────────────────────────────────────────────────────────────────────┐
│  🏆 FUTMONDO                                             [🔄 Sync] │
├──────────┬──────────────────────────────────────────────────────────┤
│          │                                                          │
│ 💰 Pres. │                                                          │
│ 📊 Evol. │              CONTENIDO PRINCIPAL                         │
│ 📈 Stats │                                                          │
│ 💰 Finan.│                                                          │
│ ⚽ Claus.│                                                          │
│ 📊 Analy.│                                                          │
│   ├ General│                                                        │
│   ├ Clasif.│                                                        │
│   ├ Jugad. │                                                        │
│   ├ Mercado│                                                        │
│   └ Proyec.│                                                        │
│          │                                                          │
├──────────┴──────────────────────────────────────────────────────────┤
```

**Responsive (< 768px):**
```
┌────────────────────────────┐
│  🏆 FUTMONDO   [☰]  [🔄] │
├────────────────────────────┤
│                            │
│   CONTENIDO FULL WIDTH     │
│                            │
└────────────────────────────┘

[☰] abre drawer overlay:
┌──────────┬─────────────────┐
│ 💰 Pres. │                 │
│ 📊 Evol. │   (backdrop     │
│ 📈 Stats │    oscuro)      │
│ 💰 Finan.│                 │
│ ⚽ Claus.│                 │
│ 📊 Analy.│                 │
│   ├ Sub..│                 │
└──────────┴─────────────────┘
```

**Pros:**
- Permite mostrar sub-navegación de Analytics sin tabs anidados
- Más espacio vertical para contenido
- Escalable: si añadimos más secciones caben fácil
- Patrón estándar en apps de gestión/admin
- Angular Material `mat-sidenav` lo soporta nativamente

**Contras:**
- Ocupa ancho lateral (~240px) en desktop
- Más complejo de implementar
- Puede sentirse "enterprise" para una app personal

---

## Opción C: Bottom Navigation Bar (estilo App Móvil)

```
┌──────────────────────────────────────────────────────────────────────┐
│  🏆 FUTMONDO                                              [🔄 Sync] │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                                                                      │
│                     CONTENIDO PRINCIPAL                              │
│                                                                      │
│                                                                      │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│   💰        📊        📈        ⚽        📊                        │
│  Presup.   Evol.    Stats    Clausul.  Analytics                    │
└──────────────────────────────────────────────────────────────────────┘
```

**Responsive (< 768px):** Igual — se mantiene el bar abajo.

**Pros:**
- Familiar para usuarios móviles
- Siempre visible sin importar scroll
- Buen uso del espacio vertical en desktop
- Material tiene componente para esto (aunque no nativo aún)

**Contras:**
- Con 6 secciones es demasiado (el máximo recomendado es 5)
- Necesitaría un botón "Más" para agrupar (Finanzas dentro de Analytics, por ejemplo)
- En desktop el bottom bar se siente raro (patrón exclusivamente mobile)
- No es estándar para dashboards de datos

---

## Opción D: Toolbar + Tabs con Hamburguesa en Móvil

```
DESKTOP:
┌──────────────────────────────────────────────────────────────────────┐
│  🏆 FUTMONDO    💰Presup. │📊Evol. │📈Stats │💰Finan│⚽Claus│📊Analy  [🔄]│
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                     CONTENIDO PRINCIPAL                              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Responsive (< 768px):**
```
┌────────────────────────────┐
│  🏆 FUTMONDO   [☰]  [🔄] │
├────────────────────────────┤
│                            │
│   CONTENIDO FULL WIDTH     │
│                            │
└────────────────────────────┘

[☰] abre dropdown/menu:
┌────────────────────────────┐
│  💰 Presupuesto           │
│  📊 Evolución             │
│  📈 Estadísticas          │
│  💰 Finanzas              │
│  ⚽ Clausulables          │
│  📊 Analytics Avanzado    │
└────────────────────────────┘
```

**Pros:**
- Compacto: todo en una sola línea en desktop
- Máximo espacio para contenido (sin sidebar, sin bottom bar)
- Responsive limpio con hamburguesa estándar
- Angular Material toolbar + mat-menu encajan perfecto

**Contras:**
- Los links de navegación en la toolbar pueden quedar apretados
- En pantallas medianas (~1024px) empieza a faltar espacio
- Menos visual que tabs con indicador de activo

---

## Resumen Comparativo

| Criterio | A (Tabs) | B (Sidebar) | C (Bottom) | D (Toolbar) |
|----------|----------|-------------|------------|-------------|
| Visibilidad opciones | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Responsive | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Espacio contenido | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Sub-nav Analytics | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| Simplicidad impl. | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Aspecto moderno | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Escalabilidad | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |

---

## 🏆 Recomendación: Opción B (Sidebar Lateral)

**Razones:**
1. Tenemos 6 secciones principales + Analytics tiene 7 sub-secciones → sidebar lo muestra todo sin agobiar
2. Se ve profesional como dashboard de datos
3. En móvil se convierte en drawer overlay (patrón estándar)
4. Si en el futuro añadimos más secciones, escala sin problema
5. Angular Material `mat-sidenav` + `mat-nav-list` lo hace trivial

**Variante propuesta:** Sidebar mini (solo iconos, ~64px) en desktop que se expande al hover o clic, para no perder tanto ancho:

```
DESKTOP (collapsed):
┌────┬─────────────────────────────────────────────────────────────────┐
│ 🏆 │  FUTMONDO                                            [🔄 Sync] │
├────┼─────────────────────────────────────────────────────────────────┤
│ 💰 │                                                                 │
│ 📊 │                                                                 │
│ 📈 │               CONTENIDO PRINCIPAL                              │
│ 💰 │                                                                 │
│ ⚽ │                                                                 │
│ 📊 │                                                                 │
└────┴─────────────────────────────────────────────────────────────────┘

DESKTOP (expanded on hover):
┌──────────────┬───────────────────────────────────────────────────────┐
│ 🏆 FUTMONDO  │                                            [🔄 Sync] │
├──────────────┼───────────────────────────────────────────────────────┤
│ 💰 Presupuesto│                                                      │
│ 📊 Evolución  │          CONTENIDO PRINCIPAL                         │
│ 📈 Estadíst.  │                                                      │
│ 💰 Finanzas   │                                                      │
│ ⚽ Clausulab. │                                                      │
│ 📊 Analytics  │                                                      │
│   ├ General   │                                                      │
│   ├ Clasific. │                                                      │
│   ├ Jugadores │                                                      │
│   ├ Mercado   │                                                      │
│   └ Proyecc.  │                                                      │
└──────────────┴───────────────────────────────────────────────────────┘
```
