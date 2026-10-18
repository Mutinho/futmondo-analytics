# Scope Document — F1: Login nativo end-to-end (app iOS Swift)

> Fase: ideación (scope-definition). Idioma: castellano; tokens técnicos verbatim en inglés.
> Fuentes: intent-statement y feasibility de F1. Scope del workflow: `feature`.

## Objetivo

Entregar un **login nativo end-to-end** en Swift/SwiftUI para la app iOS de Futmondo,
reutilizando el backend FastAPI, con el refresh token en iOS Keychain y un ajuste aditivo del
backend para transporte del refresh token (D-01).

## Dentro de alcance

1. **Ajuste aditivo del backend (D-01)**: `/auth/login` devuelve el refresh token también en el
   body; `/auth/refresh` y `/auth/logout` aceptan el refresh token por body/header, sin romper
   el canal cookie `HttpOnly` de la PWA. Con tests `pytest`.
2. **Cliente de red Swift (B-02)**: base URL configurable, serialización JSON, inyección de
   `Authorization: Bearer`, mapeo de errores (401/403/5xx/red) a tipos Swift accionables; una
   llamada de humo a `/api/v1/user/me`.
3. **Auth nativa (B-03)**: pantalla de login (email/password), intercambio por JWT, access token
   en memoria, refresh token en iOS Keychain, refresh automático (auto-login al arrancar; un
   reintento ante 401; re-login si el refresh token es inválido), logout (revoca en backend +
   borra Keychain).
4. **Polish nativo de la UI de login (SwiftUI puro, sin dependencias externas)**: animaciones
   (`matchedGeometryEffect`, `symbolEffect`, transiciones), inputs nativos con autorrelleno de
   contraseña (`.textContentType`) y foco (`@FocusState`), feedback háptico (`.sensoryFeedback`),
   materiales (`.ultraThinMaterial`), respetando Reduce Motion / Dynamic Type / VoiceOver.

## Fuera de alcance

- Pantallas de datos (Presupuesto, Mercado, Favoritos, Calculadora) → F2/F3.
- Navegación nativa / tab bar (B-08) → F2.
- **Face ID / Touch ID** para desbloquear el auto-login (`LocalAuthentication`) → mejora
  opcional **diferida** (fast-follow); amplía B-03, se decide en un intent posterior.
- Reinstalación/refirmado ~7 días (B-09), widgets (B-10), push (B-11).
- Cambios de backend más allá del transporte del refresh token (D-01).
- App Store pública, Android.

## Definición de hecho

- Backend: build + `pytest` verdes para el ajuste; gate de CI bloqueante pasado.
- Cliente nativo: validación manual documentada en el iPhone 13 Pro (login → refresh → logout);
  arnés de test de UI/dispositivo nativo como deuda registrada.
- PWA Angular existente sin regresión.

## Restricciones (ver constraint-register)

Coste 0 €; refresh token en Keychain nunca en claro; idioma inglés/castellano; gate de CI
bloqueante; cadena de build nativa `xtool` (validada en el spike F0).

## Sources

- [consumes] intent-statement, feasibility-assessment, constraint-register de F1.
- [backlog] `261016-ios-native-feasibility` (B-02, B-03, D-01).

## Assumptions & Open Questions

None.
