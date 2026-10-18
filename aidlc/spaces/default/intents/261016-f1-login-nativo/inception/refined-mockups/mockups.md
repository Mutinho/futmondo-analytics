# Mockups — F1: Login nativo (alta fidelidad, iOS SwiftUI)

> Fase: inception (refined-mockups). Alta fidelidad sobre los wireframes de ideación. Idioma:
> castellano; tokens técnicos verbatim en inglés. UI de F1: Splash + Login (ver stories US-1,
> US-3, US-6).

## Pantalla 1 — Splash / recuperación de sesión

```
+---------------------------------------+
|                                       |
|           [ logo 96pt ]               |   ← logo con matchedGeometryEffect (id: "logo")
|         Futmondo Analytics            |
|                                       |
|          ( ProgressView )             |
|        "Recuperando sesión…"          |
|                                       |
+---------------------------------------+
   fondo: degradado verde (brand) con overlay sutil
```

- Estados: cargando (ProgressView), éxito (transición a destino autenticado — placeholder en F1),
  fallo de red/5xx (aviso breve + transición a Login, sin spinner colgado), sin token (→ Login).
- Duración objetivo del refresh de arranque: feedback inmediato; sin bloquear > ~5 s sin mensaje.
- **Copy del estado `offline`**: toast/banner "No se pudo recuperar la sesión. Inicia sesión de
  nuevo." mostrado durante la transición a Login (posición: banner superior, 3 s), sin perder el
  Keychain.

## Pantalla 2 — Login

```
+---------------------------------------+
|           [ logo 64pt ]               |   ← destino del matchedGeometryEffect
|         Futmondo Analytics            |
|   Inicia sesión con tu cuenta de      |
|              Futmondo                 |
|                                       |
|  ┌─────────────────────────────────┐  |
|  │ 📧  Email                        │  |   ← TextField, .textContentType(.username)
|  └─────────────────────────────────┘  |
|  ┌─────────────────────────────────┐  |
|  │ 🔒  Contraseña            👁     │  |   ← SecureField, .textContentType(.password)
|  └─────────────────────────────────┘  |
|                                       |
|  ⚠ <mensaje de error>  (si aplica)    |   ← aparece con animación; shake del form en error
|                                       |
|  ┌─────────────────────────────────┐  |
|  │        Iniciar sesión           │  |   ← botón; ProgressView inline durante carga
|  └─────────────────────────────────┘  |
+---------------------------------------+
   tarjeta: .ultraThinMaterial, esquinas redondeadas
```

- **Email**: `TextField`, teclado `.emailAddress`, autocapitalización off, `.submitLabel(.next)`.
- **Contraseña**: `SecureField` con toggle de visibilidad (`symbolEffect` en el icono ojo),
  `.submitLabel(.go)`.
- **Botón**: deshabilitado si falta email/password o durante carga; `ProgressView` inline; haptic
  `.sensoryFeedback(.success/.error)` según resultado.
- **Error**: banner bajo los campos con texto accionable (del `detail` del backend); shake sutil
  del formulario (suprimido con Reduce Motion).
- **Variante idle**: con email o password vacíos, el botón "Iniciar sesión" se muestra
  **deshabilitado** (menor opacidad); sin banner de error.
- **Estado de foco**: el campo con foco muestra borde/realce nativo; `@FocusState` arranca en
  Email al abrir la pantalla.
- **Toggle con valor autorrellenado por iOS**: si iOS autorrellena la contraseña, el toggle de
  visibilidad sigue operando sobre el valor autorrellenado (mostrar/ocultar), sin borrarlo.

## Transiciones

- Splash → Login: `matchedGeometryEffect` del logo (96pt → 64pt) + `withAnimation`.
- Entrada de campos y botón: fade/slide corto (suprimido con Reduce Motion).

## Sources

- [consumes] wireframes.md, user-flow.md, stories.md, requirements.md, team-practices.md.

## Assumptions & Open Questions

None.
