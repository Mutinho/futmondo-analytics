# Design System Mapping — F1: Login nativo (SwiftUI)

> Fase: inception (refined-mockups). Mapea cada elemento de UI a su API nativa de Apple (sin
> dependencias de terceros, NFR-2 / P-3). Idioma: castellano; tokens técnicos verbatim en inglés.

| Elemento UI | API / componente SwiftUI (SDK Apple) | Notas |
|-------------|---------------------------------------|-------|
| Pantalla | `View` + `NavigationStack` (si aplica) | - |
| Logo con transición | `Image` + `matchedGeometryEffect` | id `"logo"` compartido Splash/Login |
| Tarjeta de login | contenedor con `.background(.ultraThinMaterial)` + `.clipShape(RoundedRectangle)` | profundidad nativa |
| Campo email | `TextField` + `.textContentType(.username)` + `.keyboardType(.emailAddress)` | autorrelleno iOS |
| Campo contraseña | `SecureField` + `.textContentType(.password)` | sugerencia de contraseña del sistema |
| Toggle visibilidad | `Button` + `Image(systemName:)` + `.symbolEffect` | SF Symbol animado |
| Foco | `@FocusState` | orden Email → Contraseña |
| Botón enviar | `Button` + `ProgressView` inline | deshabilitado por estado |
| Feedback háptico | `.sensoryFeedback(.success/.error, trigger:)` | éxito/error del login |
| Spinner splash | `ProgressView` | indeterminado |
| Fondo | `LinearGradient` (brand) | - |
| Mensaje de error | `Text` + `.transition` | texto del `detail` del backend |
| Almacén seguro | **Keychain Services** (`Security` framework) | refresh token (FR-3) |
| Red | `URLSession` | cliente de red (FR-7) |
| Biometría (diferido) | `LocalAuthentication` | solo si se activa Face ID (fuera de F1) |

Todas las APIs son del **SDK de Apple**; cero librerías de terceros (NFR-2 / P-3).

## Sources

- [consumes] mockups.md, interaction-spec.md, requirements.md (FR-3, FR-7, FR-8, NFR-2),
  team-practices.md (P-3).

## Assumptions & Open Questions

None.
