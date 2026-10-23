# Wireframes (baja fidelidad) — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, VoiceOver, Material 3) verbatim en inglés.
> Wireframes de concepto (ASCII). La referencia visual es el tema del frontend Angular (`angular-app/src/styles.scss`), reproducido en SwiftUI. Dispositivo de referencia: iPhone 13 Pro vertical.

## Pantalla 1 — Catálogo / Preview del sistema de diseño

Pantalla de desarrollo que demuestra tokens y componentes en claro/oscuro y varios tamaños de Dynamic Type. [Q1] [Q3]

```
┌─────────────────────────────┐
│  Design System · Catálogo    │  ← título (h1)
│  [ ☀︎ claro / ☾ oscuro ]  [A⇅]│  ← toggles: tema y tamaño de texto
├─────────────────────────────┤
│  COLORES                     │  ← sección (h2)
│  ● primary (verde)  ● tertiary (violeta) │
│  ● money-positive   ● money-negative     │
│   +12,5 M (verde)   −3,2 M (rojo)        │  ← ejemplo de saldo (tokens semánticos)
│  ▦ surface / on-surface  ▦ splash grad.  │
├─────────────────────────────┤
│  TIPOGRAFÍA                  │  ← sección (h2)
│  H1 Título grande            │
│  H2 Subtítulo                │
│  H3 Encabezado menor         │
│  Body · Roboto · Dynamic Type│
├─────────────────────────────┤
│  ESPACIADO                   │  ← sección (h2)
│  xs · sm · md · lg · xl      │
├─────────────────────────────┤
│  COMPONENTES                 │  ← sección (h2)
│  [ Botón primario ]          │
│  ┌ Campo de texto ─────────┐ │
│  │ Email            ✉       │ │
│  └──────────────────────────┘ │
│  ┌ Tarjeta ────────────────┐ │
│  │  contenido de ejemplo    │ │
│  └──────────────────────────┘ │
│  ◌ Cargando…    ⚠ Error      │  ← estados de carga/error
└─────────────────────────────┘
```

**Accesibilidad**: h1 "Design System · Catálogo"; landmark `main` con secciones como encabezados `h2`; punto de entrada de foco/teclado en los toggles de tema/tamaño (primer elemento interactivo); navegación por scroll vertical; todos los componentes con etiqueta VoiceOver; Dynamic Type activo; contraste verificado en claro/oscuro. [Q6]

## Pantalla 2 — Login de F1 revestido

Mismo comportamiento que el login de F1 ya construido (sin cambios funcionales), revestido con el sistema. Layout basado en el login de referencia de Angular (`login.component.ts`): card centrada sobre gradiente verde. [Q1]

```
┌─────────────────────────────┐
│    (gradiente verde splash)  │
│                              │
│      ┌──────────────────┐    │
│      │     [logo 64]     │   │  ← logo
│      │ Futmondo Analytics│   │  ← h1
│      │ Inicia sesión…    │   │  ← subtítulo
│      │ ┌ Email ───── ✉ ┐ │   │  ← campo (componente del sistema)
│      │ └──────────────┘ │   │
│      │ ┌ Contraseña 🔒👁┐│   │  ← campo + toggle visibilidad
│      │ └──────────────┘ │   │
│      │ ⚠ (error si hay) │   │  ← estado de error (componente)
│      │ [ Iniciar sesión ]│   │  ← botón primario (+ spinner al cargar)
│      └──────────────────┘    │
└─────────────────────────────┘
```

**Accesibilidad**: h1 "Futmondo Analytics"; landmark `main` con la card de login; punto de entrada de teclado en el campo Email; campos con etiqueta VoiceOver; botón primario con estado de carga anunciable; contraste del texto sobre card en claro/oscuro. [Q6]

## Assumptions & Open Questions

- [assumption] El mapeo exacto de roles de color Material 3 → SwiftUI y de la escala tipográfica (`h1/h2/h3` → estilos nativos) se concreta en refined-mockups / diseño; aquí es conceptual. [Q4]
