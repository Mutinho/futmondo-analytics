# Interaction Spec — Componentes del sistema de diseño (SwiftUI)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Especificación a nivel de componente (estados, interacción, tokens consumidos). Base: `design-system-mapping.md`.

## PrimaryButton — [FR4.1]

- **Props**: título, acción, `isLoading`, `isEnabled`.
- **Estados**:
  - Normal: fondo `primary`, texto `onPrimary`, corner radius 12, altura 48 pt.
  - Loading: muestra spinner centrado; deshabilita la pulsación; conserva tamaño.
  - Disabled: opacidad reducida; sin acción.
- **Interacción**: tap ejecuta la acción salvo en loading/disabled. Área táctil ≥44 pt. VoiceOver: rol button, label = título, estado "cargando" anunciado. [NFR1]

## TextInputField — [FR4.2]

- **Props**: label, texto (binding), icono opcional (prefix), `isSecure`, mensaje de error opcional.
- **Estados**: normal (borde `onSurfaceVariant`), foco (borde `primary`), error (borde + texto `moneyNegative`/error, mensaje bajo el campo), secure con toggle de visibilidad.
- **Interacción**: edición de texto; toggle de visibilidad en secure; teclado adecuado (email/password). VoiceOver: label asociado, error anunciado. [NFR1]

## Card — [FR4.3]

- Superficie `surface`, corner radius 16, sombra sutil; contiene contenido arbitrario. Respeta espaciado interno `md`.

## LoadingState / ErrorState — [FR4.4]

- **LoadingState**: spinner + texto opcional; usado en pantallas y en el botón.
- **ErrorState**: icono ⚠ + mensaje con fondo `errorContainer`, texto de error; reutilizable.

## Catálogo — controles — [FR5.2]

- **Toggle de tema**: segmented control claro/oscuro; cambia el `colorScheme` del preview.
- **Control de tamaño de texto**: ajusta el `dynamicTypeSize` del preview (p. ej. de `.small` a `.accessibility3`).

## Assumptions & Open Questions

None.
