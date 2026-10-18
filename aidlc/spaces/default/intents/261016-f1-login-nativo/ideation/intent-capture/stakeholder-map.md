# Stakeholder Map — F1: Login nativo end-to-end

> Fase: ideación (intent-capture). Idioma: castellano; tokens técnicos verbatim en inglés.

## Actores

| Actor | Rol en F1 | Interés / expectativa |
|-------|-----------|------------------------|
| Propietario-ejecutor (tú) | Decisor y desarrollador único | Login nativo funcional en el iPhone 13 Pro, a coste 0 €, aprendiendo Swift/SwiftUI; sin romper la PWA en producción. |
| Usuario final de la app nativa | Consumidor del login | Iniciar sesión con sus credenciales Futmondo y mantener la sesión sin fricción (refresh transparente). |
| Backend FastAPI (`futmondo-api`) | Sistema reutilizado | Autentica contra Futmondo, emite JWT, gestiona refresh/logout; recibe un **ajuste aditivo** (D-01) sin regresión para la PWA. |
| PWA Angular existente | Sistema hermano en producción | No sufrir regresión: el canal cookie `HttpOnly` de login/refresh/logout debe seguir intacto. |
| API Futmondo (externa) | Autoridad de credenciales | El backend valida las credenciales contra ella; F1 no la toca directamente. |
| Gate de CI (GitHub Actions) + Fly.io | Control de calidad y despliegue | Cualquier cambio de backend pasa el gate bloqueante antes de `main`/producción. |

## Especificaciones de referencia (no se portan, se consultan)

- `angular-app/src/app/features/login/login.component.ts` — UX y flujo de login.
- `angular-app/src/app/core/services/auth.service.ts` + `auth.interceptor` — flujo de
  access/refresh y adjunto de `Authorization` (a leer en inception).
- `backend/app/auth/routes.py` — contrato real de `/auth/login|refresh|logout`.

## Límites de responsabilidad

- F1 **produce**: cliente de red Swift + auth nativa (login, refresh, Keychain, logout) + el
  ajuste aditivo de backend para D-01.
- F1 **no produce**: pantallas de datos, navegación, ni cambios de infra/despliegue.

## Sources

- [backlog] `261016-ios-native-feasibility/.../intent-backlog.md` (actores: ejecutor único,
  sin coordinación multi-equipo).
- [feasibility] `261016-ios-native-feasibility/.../feasibility-assessment.md` §5 (backend,
  PWA, D-01).
- [code] `backend/app/auth/routes.py`.

## Assumptions & Open Questions

None.
