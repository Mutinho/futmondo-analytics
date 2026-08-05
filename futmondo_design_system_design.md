# Design System: Futmondo UX/UI Improved

## 1. Concepto Visual
- **Estilo:** Moderno, limpio y profesional, basado en **Angular Material 22**.
- **Atmósfera:** Una herramienta de gestión deportiva que equilibra la densidad de datos con una jerarquía visual clara y "aire" (whitespace) para reducir la carga cognitiva.
- **Paleta de Colores:**
    - **Primario:** Verde Futmondo (`#4CAF50` o similar, usado en estados activos y acentos positivos).
    - **Superficie (Background):** Blanco puro para contenedores y un gris muy claro (`#f8f9fa`) para el fondo general de la aplicación.
    - **Textos:**
        - Énfasis alto: `#1a1a1a` (Nombres de jugadores, títulos).
        - Énfasis medio: `#666666` (Datos secundarios, etiquetas de tabla).
    - **Semántica:**
        - Positivo (Subidas/Rendimiento): Verde desaturado (`#2e7d32`).
        - Negativo (Saldos/Bajadas): Rojo "soft" o desaturado (`#d32f2f`) para evitar el ruido visual excesivo.
        - Crítico: Rojo vibrante solo para bloqueos de cuenta.

## 2. Layout y Estructura
### Barra Lateral (Sidebar)
- **Ancho:** 240px.
- **Fondo:** Blanco con un borde lateral derecho sutil (`1px solid #e0e0e0`).
- **Navegación:** 
    - Botones con `border-radius: 8px` o `pill-shape`.
    - Estado Activo: Fondo verde menta muy suave (`rgba(76, 175, 80, 0.1)`) y una barra vertical de 4px en el extremo izquierdo del botón.
    - Iconografía: Material Symbols Outlined, tamaño 20px.
- **Header del Sidebar:** Logo de Futmondo con espaciado generoso (padding: 24px).

### Contenedor Principal
- **Padding:** 32px para permitir que el contenido respire.
- **Gaps:** Espaciado consistente de 24px entre componentes (cards, tablas, headers).

## 3. Componentes de UI (Angular Material 22)
### Tablas (`mat-table`)
- **Densidad:** `display-density: comfortable`. Padding lateral de celdas: 16px.
- **Headers:** Tipografía en gris medio, `font-size: 12px`, `font-weight: 600`, `text-transform: capitalize`.
- **Filas:** Borde inferior sutil (`1px solid rgba(0,0,0,0.08)`). Sin bordes verticales.
- **Jerarquía en Filas:** 
    - Columna de Nombre: `font-weight: 600`, color oscuro.
    - Datos secundarios bajo el nombre: `font-size: 12px`, color gris.
- **Resaltado:** La columna de acción principal (ej. "Puja Sugerida" o "Rendimiento") debe tener un peso mayor (`font-weight: 700`) y un color que la diferencie.

### Chips de Posición
- **Forma:** Circulares o redondeados (pill-shaped).
- **Tamaño:** Pequeños para no competir con el texto.
- **Colores sugeridos:**
    - Portero (PO): Amarillo suave.
    - Defensa (DF): Ocre/Marrón suave.
    - Mediocentro (MC): Azul suave.
    - Delantero (DL): Rojo/Naranja suave.

### Tarjetas de Resumen (Dashboard Cards)
- **Elevación:** `mat-elevation-z1` o `z0` con borde sutil.
- **Grid:** Layout de 4 columnas para datos de presupuesto.
- **Labels:** Arriba, pequeñas y en gris. **Valores:** Abajo, grandes, con tipografía numérica clara y colores semánticos aplicados.

## 4. Tipografía
- **Fuente:** Sans-serif (preferiblemente Inter o Roboto).
- **Escala:**
    - Títulos de página: 28px, `font-weight: 700`.
    - Encabezados de sección: 20px, `font-weight: 600`.
    - Body: 14px.
    - Datos técnicos/Tablas: 13px o 14px.

## 5. Interacciones y Estados
- **Hover en Tablas:** Cambio sutil de fondo (`#f5f5f5`) para indicar interactividad.
- **Botones de Acción:** Redondeados, con elevación baja.
- **Indicadores de Tendencia:** Iconos de flecha (`arrow_drop_up`, `arrow_drop_down`) integrados junto al valor numérico, usando los colores semánticos definidos.
