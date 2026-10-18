# Feasibility Assessment — F1: Login nativo end-to-end (app iOS Swift)

> Fase: ideación (feasibility). Perspectiva de arquitectura. Idioma: castellano; tokens
> técnicos verbatim en inglés. Estimaciones conservadoras; supuestos marcados. Fuentes:
> intent-statement de F1 y lectura directa del backend (`jwt_utils.py`, `dependencies.py`,
> `auth/routes.py`) y del cliente Angular (`core/services/auth.service.ts`).

## 1. Veredicto

**GO.** F1 es técnicamente viable y de riesgo bajo. Las dos incógnitas que el intent-statement
dejó abiertas se han **cerrado por lectura de código**, no por suposición:

- El **formato del JWT es estándar y reutilizable** por un cliente nativo sin cambios (R
  eliminado).
- La dependencia **D-01 queda acotada a transporte del refresh token** (ajuste aditivo del
  backend), no al formato ni a la emisión del token.

## 2. Hechos verificados (base de la viabilidad)

### 2.1 Formato y emisión del token (`backend/app/auth/jwt_utils.py`)

- Access token: JWT `HS256` firmado con `JWT_SECRET`, claims `sub`, `email`, `futmondo_uid`,
  `type:"access"`, `iat`, `exp` (60 min), `jti`.
- Refresh token: JWT `HS256`, claims `sub`, `type:"refresh"`, `iat`, `exp` (30 días), `jti`;
  se persiste su `sha256` para revocación.
- Un cliente Swift **no necesita decodificar** el access token: lo guarda y lo reenvía. El
  formato es estándar → el supuesto `[assumption]` del intent-statement sobre el JWT **se
  confirma**: F1 no toca el formato ni la emisión.

### 2.2 Validación del Bearer (`backend/app/auth/dependencies.py`)

- `get_current_user` lee `Authorization: Bearer <token>` del header y verifica `type:"access"`.
- Las llamadas protegidas a `/api/v1/*` desde el cliente nativo **ya encajan sin cambios de
  backend**; sólo requieren adjuntar el header.

### 2.3 Transporte del refresh token — D-01 (`auth/routes.py` + `auth.service.ts`)

- `/auth/login` fija el refresh token en cookie `HttpOnly` (`futmondo_refresh_token`,
  `path=/auth`, `samesite=lax`) y **no lo devuelve en el body**.
- `/auth/refresh` y `/auth/logout` leen el refresh token **sólo de esa cookie**.
- La PWA Angular usa `withCredentials: true` en los tres endpoints (canal cookie).
- Conclusión: el ajuste nativo es **puro transporte** — (a) devolver el refresh token también
  en el body del login, (b) aceptarlo por body/header en refresh/logout — **aditivo**, dejando
  intacto el canal cookie de la PWA.

## 3. Viabilidad por dimensiones

- **Técnica**: alta. El contrato de token y el header Bearer ya son nativo-compatibles; sólo
  falta el ajuste aditivo de transporte + el cliente Swift + Keychain. SwiftUI/URLSession cubren
  de sobra la capa de red/auth.
- **Económica**: coste 0 € (sin dependencias de pago; Keychain y URLSession son del SDK; firma
  gratuita ya validada en el spike F0).
- **De esfuerzo**: moderada — un ajuste pequeño de backend con tests + una capa de red/auth
  nueva en Swift. Sin plazo.
- **De seguridad**: el refresh token va a **iOS Keychain** (regla durable); el ajuste de
  backend no debilita el canal cookie `HttpOnly` ni la revocación por `sha256`.

## 4. Opciones del ajuste D-01 (a decidir en diseño, no aquí)

El intent-statement fijó Q1=A (aditivo). El **cómo** fino (header propio vs. `Authorization`
vs. body JSON; mismo endpoint vs. negociación) se resuelve en contract-design/functional-design.
La viabilidad no depende de cuál se elija: todas son aditivas y de bajo riesgo.

## Sources

- [consumes] `261016-f1-login-nativo/ideation/intent-capture/intent-statement.md`.
- [code] `backend/app/auth/jwt_utils.py` (formato/emisión del JWT), verificado en esta etapa.
- [code] `backend/app/auth/dependencies.py` (validación del Bearer por header).
- [code] `backend/app/auth/routes.py` (login/refresh/logout por cookie `HttpOnly`).
- [code] `angular-app/src/app/core/services/auth.service.ts` (flujo de refresh de referencia,
  `withCredentials: true`).
- [memory:M1] Coste 0 € con excepción acotada de distribución nativa.
- [memory:M2] Refresh token en iOS Keychain, nunca en claro.

## Assumptions & Open Questions

None.
