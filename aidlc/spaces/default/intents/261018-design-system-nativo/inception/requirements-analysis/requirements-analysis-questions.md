# Requirements Analysis — Preguntas de clarificación

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, Material 3, VoiceOver, Apple HIG) verbatim en inglés.
> Requisitos del sistema de diseño nativo iOS. Las opciones por defecto reflejan la ideación ya aprobada. Rellena cada `[Answer]:`.

## Q1. Alcance de los tokens de color — ¿qué roles del tema de Angular se reproducen como tokens SwiftUI?

- A. Roles semánticos clave: primary (verde), tertiary (violeta), surface/on-surface y variantes, más los tokens propios `money-positive`/`money-negative` y el gradiente de splash; en claro y oscuro. (Cobertura suficiente para login + futuras pantallas de datos.)
- B. Sólo primary + surface + money-positive/negative (mínimo).
- C. Todos los roles `--mat-sys-*` de Material 3 uno a uno.
- X. Other (please specify)

[Answer]: A. Roles semánticos clave (primary verde, tertiary violeta, surface/on-surface + variantes, money-positive/negative, gradiente de splash) en claro y oscuro.

## Q2. Tipografía — ¿qué exige el sistema?

- A. Escala `h1/h2/h3` + body basada en Roboto, con soporte Dynamic Type (el texto escala con los ajustes del sistema). Si Roboto no está disponible como fuente empaquetada, fallback a la fuente del sistema con la misma escala.
- B. Igual que A pero empaquetando Roboto obligatoriamente.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Escala h1/h2/h3 + body basada en Roboto con Dynamic Type; fallback a la fuente del sistema con la misma escala si Roboto no está empaquetada.

## Q3. Componentes base — ¿cuáles y con qué estados?

- A. Botón (primario; estados normal/disabled/loading), campo de texto (con label, icono opcional, estado de error), tarjeta (superficie contenedora) y estados de carga/error reutilizables. Cada uno respeta tokens y claro/oscuro.
- B. Igual que A más variantes secundarias de botón (texto/outline) ya en este intent.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Botón (primario; normal/disabled/loading), campo de texto (label, icono opcional, estado de error), tarjeta y estados de carga/error reutilizables; todos respetan tokens y claro/oscuro.

## Q4. Revestir el login de F1 — ¿qué criterio de "sin regresión"?

- A. El login revestido conserva el comportamiento funcional de F1 (login → auto-login → logout, validación, mensajes de error) sin cambios; sólo cambia la capa visual, verificable manualmente en el iPhone 13 Pro.
- B. Igual que A más una verificación automatizada mínima.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. El login revestido conserva el comportamiento de F1 (login → auto-login → logout, validación, mensajes de error); sólo cambia la capa visual, verificable manualmente en el iPhone 13 Pro.

## Q5. NFR de accesibilidad — ¿qué nivel exigimos como requisito?

- A. Dynamic Type soportado en todos los componentes; contraste de color suficiente en claro/oscuro; VoiceOver con etiquetas/roles correctos en los componentes base. Objetivo informal alineado con WCAG AA donde aplique a móvil nativo (sin herramienta de auditoría de pago).
- B. Sólo Dynamic Type + contraste (VoiceOver diferido).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Dynamic Type en todos los componentes; contraste suficiente en claro/oscuro; VoiceOver con etiquetas/roles correctos en los componentes base; objetivo informal WCAG AA donde aplique a móvil nativo.

## Q6. NFR de coste y dependencias — ¿confirmamos el guardarraíl?

- A. Sí: sólo SDK de Apple, coste 0 € recurrente, sin dependencias de pago ni tooling de diseño de pago (regla durable del proyecto).
- B. Not applicable.
- X. Other (please specify)

[Answer]: A. Sí: sólo SDK de Apple, coste 0 € recurrente, sin dependencias de pago ni tooling de diseño de pago.

## Q7. Pantalla de catálogo/preview — ¿qué debe demostrar como criterio de aceptación?

- A. Muestra todos los tokens (colores, tipografía, espaciado) y todos los componentes base, con control para alternar claro/oscuro y tamaño de Dynamic Type, verificable de un vistazo contra el tema de Angular.
- B. Igual que A pero sin control de tamaño de texto (sólo claro/oscuro).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Muestra todos los tokens y componentes base con control para alternar claro/oscuro y tamaño de Dynamic Type, verificable contra el tema de Angular.

## Q8. ¿Algo explícitamente fuera de los requisitos de este intent?

- A. Fuera: tab bar/navegación nativa (F2), aplicación del sistema a pantallas de datos de F2, animaciones/microinteracciones avanzadas, temas más allá de claro/oscuro, arnés de test de UI nativo (diferido), y cualquier cambio de backend/CI.
- B. Quiero ajustar (indica cómo).
- X. Other (please specify)

[Answer]: A. Fuera: tab bar/navegación nativa (F2), aplicación a pantallas de datos de F2, animaciones/microinteracciones avanzadas, temas más allá de claro/oscuro, arnés de test de UI nativo (diferido) y cualquier cambio de backend/CI.

## Consolidated Summary Confirmation

Resumen de tus respuestas de Requirements Analysis:

- **Tokens de color (Q1=A)**: roles semánticos clave del tema Angular (primary verde, tertiary violeta, surface/on-surface, money-+/-, splash) en claro y oscuro.
- **Tipografía (Q2=A)**: escala h1/h2/h3 + body Roboto con Dynamic Type; fallback a fuente del sistema si Roboto no se empaqueta.
- **Componentes (Q3=A)**: botón, campo, tarjeta, estados de carga/error; consumen tokens y claro/oscuro.
- **Revestir F1 (Q4=A)**: sin cambios de comportamiento; verificación manual en iPhone 13 Pro.
- **Accesibilidad (Q5=A)**: Dynamic Type + contraste + VoiceOver; WCAG AA informal.
- **Coste (Q6=A)**: sólo SDK de Apple, coste 0 €, sin dependencias de pago.
- **Catálogo (Q7=A)**: muestra tokens y componentes con toggles claro/oscuro y tamaño de texto.
- **Fuera (Q8=A)**: tab bar/F2, pantallas de F2, animaciones avanzadas, temas extra, arnés de test nativo, backend/CI.

Requisitos: FR1 (color), FR2 (tipografía), FR3 (espaciado), FR4 (componentes), FR5 (catálogo), FR6 (revestir F1); NFR1 accesibilidad, NFR2 coste, NFR3 fidelidad, NFR4 dispositivo.

¿Does this all look correct before I generate the requirements artifact?

[Answer]: Looks correct
