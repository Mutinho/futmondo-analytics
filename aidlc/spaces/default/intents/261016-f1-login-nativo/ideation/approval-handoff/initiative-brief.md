# Initiative Brief — F1: Login nativo end-to-end (app iOS Swift)

> One-pager de cierre de ideación. Fuentes: todos los artefactos de ideación de F1. Idioma:
> castellano; tokens técnicos verbatim en inglés.

## Intent y problema

Entregar la **primera capa funcional (F1)** de la app iOS nativa de Futmondo: un **login nativo
end-to-end** en Swift/SwiftUI que autentique contra el backend FastAPI existente, con el refresh
token en iOS Keychain. Es el siguiente eslabón risk-first tras el spike F0 (`xtool`, ya
validado): sin red + auth no hay pantallas (F2 depende de esto).

## Qué incluye F1

- **Ajuste aditivo del backend (D-01)**: login devuelve el refresh token también en el body;
  refresh/logout lo aceptan por body/header, sin romper el canal cookie `HttpOnly` de la PWA.
- **Cliente de red Swift (B-02)**: base URL, JSON, inyección de `Bearer`, errores tipados +
  llamada de humo a `/api/v1/user/me`.
- **Auth nativa (B-03)**: login, access token en memoria, refresh token en Keychain, refresh
  automático (un reintento ante 401; re-login si falla), logout.
- **Polish nativo del login (SwiftUI puro, coste 0 €)**: animaciones, autorrelleno de contraseña
  de iOS, haptics, materiales; respetando Reduce Motion / Dynamic Type / VoiceOver.

## Validación de la viabilidad (hechos verificados)

- Formato del JWT estándar `HS256` reutilizable sin cambios (`jwt_utils.py`).
- `Authorization: Bearer` ya validado por header (`dependencies.py`) → `/api/v1/*` encaja.
- D-01 acotado a **transporte** del refresh token (lectura de `auth/routes.py` + `auth.service.ts`).
- Entorno de build nativo (WSL + Swift 6.4 + `xtool` + Apple ID) satisfecho por el spike F0.

## Frontera de alcance

- **Dentro**: ajuste backend D-01, cliente de red, auth nativa, polish nativo del login.
- **Fuera**: pantallas de datos y navegación/tab bar (F2); Face ID/Touch ID (diferido, amplía
  B-03); refirmado ~7 días (B-09); widgets (B-10); push (B-11); cambios de backend fuera de D-01;
  App Store pública; Android.

## Riesgos principales (ver raid-log)

- Regresión del canal cookie de la PWA por el ajuste aditivo → mitigado con tests `pytest` y gate
  de CI.
- Manejo del Keychain → criterio de hecho explícito + revisión de seguridad en diseño.

## Coste

0 € recurrente (SDK de Apple, firma gratuita; sin dependencias de pago; librerías OSS a versión
exacta si hiciera falta alguna).

## Definición de hecho

Backend: build + `pytest` verdes + gate de CI. Cliente nativo: validación manual en el iPhone 13
Pro (login → refresh → logout); arnés de test nativo como deuda registrada. PWA sin regresión.

## Recomendación

**GO.** Ideación cerrada; F1 viable y de riesgo bajo. Siguiente fase: inception
(reverse-engineering del backend de auth y del cliente de referencia).

## Sources

- [consumes] intent-statement, stakeholder-map, scope-document, intent-backlog,
  feasibility-assessment, constraint-register, wireframes de F1.

## Assumptions & Open Questions

None.
