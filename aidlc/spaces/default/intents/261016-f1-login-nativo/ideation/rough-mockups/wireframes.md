# Wireframes — F1: Login nativo (iOS SwiftUI)

> Fase: ideación (rough-mockups). Wireframes de baja fidelidad. Idioma: castellano; tokens
> técnicos verbatim en inglés. Alcance de UI de F1: **sólo** la pantalla de Login y el Splash de
> auto-login (el resto de F1 —cliente de red, Keychain, ajuste de backend— no tiene UI). Fuente
> de referencia: `angular-app/src/app/features/login/login.component.ts`.

## Pantalla 1 — Splash / recuperación de sesión

```
+---------------------------------------+
|                                       |
|              [ logo ]                 |
|          Futmondo Analytics           |
|                                       |
|            ( spinner )                |
|        Recuperando sesión…            |
|                                       |
+---------------------------------------+
```

- Al arrancar la app: si hay refresh token en Keychain, intenta refresh automático
  (auto-login). Mientras tanto muestra el splash.
- Éxito → navega a la primera pantalla autenticada (en F1, el destino es placeholder; las
  pantallas reales llegan en F2).
- Fallo/ausencia de token → navega a Login.
- **Fallo de red durante el refresh**: no se queda colgado en el spinner; tras el fallo, muestra
  un aviso breve y cae a Login (nunca un spinner indefinido).

## Pantalla 2 — Login

```
+---------------------------------------+
|              [ logo ]                 |
|          Futmondo Analytics           |
|   Inicia sesión con tu cuenta de      |
|              Futmondo                 |
|                                       |
|  Email                                |
|  [ 📧  tu@email.com               ]   |
|                                       |
|  Contraseña                           |
|  [ 🔒  ••••••••              👁 ]     |
|                                       |
|  ( ! mensaje de error, si lo hay )    |
|                                       |
|  [       Iniciar sesión        ]      |
|            ( spinner si carga )       |
+---------------------------------------+
```

Elementos y estados (espejo de la PWA, en controles nativos SwiftUI):
- Campo **Email**: teclado tipo email, autocapitalización off.
- Campo **Contraseña**: seguro (oculto) con toggle de visibilidad.
- Botón **Iniciar sesión**: deshabilitado si falta email o password, o si hay carga en curso;
  muestra spinner mientras valida.
- **Mensaje de error**: visible bajo los campos cuando el backend responde 401 u otro fallo;
  texto accionable en castellano (p. ej. "Credenciales incorrectas…").
- Accesibilidad: labels asociadas a cada campo; contraste suficiente; el toggle de visibilidad
  con etiqueta accesible ("Mostrar/Ocultar contraseña"); orden de foco Email → Contraseña →
  Iniciar sesión.

## Logout (no es pantalla propia en F1)

El logout se dispara desde un control (en F2 vivirá en la navegación); en F1 basta una acción
accesible que invoque `/auth/logout`, borre el Keychain y vuelva a Login. **En F1 el logout no
tiene superficie de UI dedicada**: su punto de entrada es provisional/placeholder, no UI
pendiente.

## Polish nativo (dentro de F1 — SwiftUI puro, coste 0 €, sin dependencias externas)

F1 no "copia" la pantalla de la PWA: aprovecha lo nativo con **sólo SDK de Apple** (sin Lottie
ni librerías de animación de terceros). Mejoras de la pantalla de Login y el Splash:

- **Transición splash → login**: `matchedGeometryEffect` para que el logo del splash "viaje" a
  su posición en el login; `withAnimation` para la aparición de campos y botón.
- **Iconos animados**: `symbolEffect` sobre SF Symbols (candado que se cierra, ojo del toggle de
  contraseña al mostrar/ocultar).
- **Inputs nativos**: `TextField`/`SecureField` con `.textContentType(.username)` /
  `.textContentType(.password)` para **autorrelleno y sugerencia de contraseña de iOS**
  (la superposición de autorrelleno la pinta el sistema; no requiere UI propia en el wireframe);
  `@FocusState` para el foco programático Email → Contraseña; `.submitLabel(.go)`; teclado
  tipo email.
- **Feedback háptico**: `.sensoryFeedback` sutil en éxito (success) y en error (error) del login.
- **Materiales y profundidad**: fondo con degradado y `.ultraThinMaterial` en la tarjeta.
- **Estado del botón**: progreso animado durante la validación; shake sutil del formulario en
  error de credenciales.
- **Respeto a accesibilidad**: **todas** las animaciones —incluidos el shake del formulario y los
  `symbolEffect`— respetan **Reduce Motion** (se degradan a transiciones instantáneas / sin
  movimiento); Dynamic Type y VoiceOver soportados.

## Mejora opcional / diferida (NO en F1) — Face ID / Touch ID

Desbloqueo biométrico del auto-login con el framework `LocalAuthentication` (SDK de Apple,
coste 0 €): al arrancar, antes de usar el refresh token del Keychain, pedir Face ID/Touch ID.
Es una **capacidad de seguridad nueva** que amplía B-03, por lo que se documenta como mejora
opcional **diferida** (fast-follow); se decide su entrada en un intent posterior, no en F1.
Nota de diseño para cuando se implemente: si el biométrico se cancela o no está disponible,
**fallback a login manual**, preservando la garantía de que el refresh token sólo vive en el
Keychain (nunca en claro).

## Sources

- [consumes] intent-statement, scope-document, intent-backlog de F1.
- [code] `angular-app/src/app/features/login/login.component.ts` (campos, estados, textos de
  referencia).

## Assumptions & Open Questions

None.
