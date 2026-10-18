# Interaction Spec — F1: Login nativo

> Fase: inception (refined-mockups). Especificación de interacción. Idioma: castellano; tokens
> técnicos verbatim en inglés.

## Estados de la pantalla de Login

| Estado | Disparador | UI | Traza |
|--------|-----------|----|-------|
| idle | pantalla abierta | campos vacíos, botón deshabilitado | US-1 |
| typing | el usuario escribe | botón habilitado cuando email y password no vacíos | US-1 |
| loading | pulsa "Iniciar sesión" | botón con `ProgressView`, campos deshabilitados | US-1 |
| error | login 401/otro fallo | banner de error + shake (si no Reduce Motion) + haptic error | US-1 |
| success | login 200 | haptic success + transición a destino autenticado | US-1 |

## Estados del Splash

| Estado | Disparador | UI | Traza |
|--------|-----------|----|-------|
| checking | arranque con token en Keychain | `ProgressView` + "Recuperando sesión…" | US-3 |
| resumed | refresh 200 | transición a destino autenticado | US-3 |
| expired | refresh 401/revocado | borra Keychain → Login | US-3 |
| offline | fallo de red/5xx | aviso breve → Login; Keychain preservado | US-3 |
| no-session | sin token en Keychain | → Login directo | US-3 |

## Transiciones y feedback

- `matchedGeometryEffect(id: "logo")` entre Splash y Login.
- Aparición de campos: transición corta; **suprimida con Reduce Motion**.
- `symbolEffect` en el icono del toggle de contraseña al mostrar/ocultar.
- `.sensoryFeedback(.success)` al login OK; `.sensoryFeedback(.error)` al fallo.
- Shake del formulario en error de credenciales; **suprimido con Reduce Motion**.

## Refresh ante 401 (interacción invisible)

- Llamada protegida → 401 → refresh con token del Keychain → reintento **único** de la petición.
- Si el reintento vuelve a 401 o el refresh falla por 401/revocación → re-login (sin bucle).
  (US-4)
- **UX percibida**: el refresh invisible no bloquea la UI; si supera ~1 s, la pantalla en curso
  muestra su indicador de carga propio (no un modal). No se muestra pantalla de login salvo que el
  refresh falle de forma terminal.

## Sources

- [consumes] mockups.md, user-flow.md, stories.md (US-1, US-3, US-4, US-6).

## Assumptions & Open Questions

None.
