# Intent Capture — Preguntas de encuadre (F1: Login nativo end-to-end)

> Responde escribiendo tu elección en el tag de respuesta de cada pregunta (una letra; o `X`
> con texto libre). Puedes contestar en modo guiado (una a una), auto-guiado (editas este
> fichero) o chat (me lo dices y yo lo relleno). Las respuestas encuadran F1 antes de cerrar
> intent-capture; el **cómo** fino se decide en diseño (inception/construcción).

---

## Q1 — Estrategia del ajuste de backend para D-01 (transporte del refresh token)

`/auth/refresh` hoy lee el refresh token sólo de la cookie `HttpOnly`, y `/auth/login` no lo
devuelve en el body. Un cliente nativo necesita otra vía. ¿Cómo encuadramos el ajuste?

- A. **Aditivo por body/header, canal cookie intacto** (recomendado): `/auth/refresh` acepta
  además el refresh token por header (p. ej. `Authorization`/header propio) o body; `/auth/login`
  lo devuelve también en el body JSON. La PWA sigue usando la cookie sin cambios. Mínima
  superficie, sin regresión.
- B. Endpoints nuevos dedicados a nativo (p. ej. `/auth/native/*`) separados de los de la PWA.
- C. Negociar por cabecera/flag de cliente (misma ruta, comportamiento según tipo de cliente).
- X. Other (please specify)

[Answer]: A

---

## Q2 — Alcance del cliente de red Swift (B-02) en F1

¿Hasta dónde llega el cliente HTTP en F1?

- A. **Núcleo auth-first** (recomendado): base URL + JSON + inyección de `Bearer` + manejo de
  errores tipados, ejercitado contra `/auth/*` y **una** llamada protegida de humo a `/api/v1/*`
  (p. ej. `/api/v1/user/me`) para probar el token end-to-end. El resto de endpoints llegan con
  sus pantallas en F2.
- B. Cliente genérico completo para todos los `/api/v1/*` ya en F1 (más alcance, menos risk-first).
- C. Sólo `/auth/*`, sin ninguna llamada protegida en F1.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Estrategia de almacenamiento/refresh del token en el cliente nativo

El refresh token va a **iOS Keychain** (regla durable). ¿Y el access token y el refresco?

- A. **Access token en memoria + refresh token en Keychain + refresh automático** (recomendado,
  espeja la PWA): al arrancar la app, si hay refresh token en Keychain, se intenta refrescar
  (auto-login silencioso); el interceptor refresca ante un 401 y reintenta una vez.
- B. Access y refresh ambos en Keychain (persistir también el access).
- C. Sin refresh automático en F1 (login manual siempre que caduque; refresh queda para después).
- X. Other (please specify)

[Answer]: A

---

## Q4 — ¿Cuánto del ajuste de backend (D-01) entra en ESTE intent F1?

- A. **El ajuste aditivo completo de login/refresh/logout + sus tests** entra en F1 (recomendado:
  F1 queda realmente end-to-end y verificable).
- B. Sólo `/auth/refresh` (lo imprescindible para el refresh); login por body y logout después.
- C. El ajuste de backend se saca a un intent propio y F1 asume que ya existe.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Verificación / "definición de hecho" de F1

¿Cómo damos F1 por terminado?

- A. **Build + tests de backend (pytest) verdes para el ajuste, y validación manual en el
  iPhone** (login → refresh → logout) documentada (recomendado para un cliente nativo sin arnés
  de test de dispositivo todavía). El test automatizado de UI/dispositivo nativo queda para
  cuando exista arnés (deuda registrada).
- B. Además de A, montar ya un arnés de test unitario Swift (XCTest) para la capa de red/auth.
- C. Sólo validación manual en el dispositivo, sin tests nuevos de backend.
- X. Other (please specify)

[Answer]: A

---

## Q6 — ¿Algo que quieras AÑADIR o SACAR del alcance de F1?

Texto libre (p. ej. manejo de errores de red offline, biometría/FaceID para desbloquear el
Keychain, pantalla de splash de auto-login, etc.). Si nada, deja `None`.

[Answer]: None

---

## Consolidated Summary Confirmation

Antes de cerrar intent-capture, confirma que este encuadre de F1 es correcto:

- **Q1 — Ajuste D-01 del backend**: A) aditivo — `/auth/refresh` acepta el refresh token por
  header/body y `/auth/login` lo devuelve también en el body; la cookie `HttpOnly` del
  navegador queda intacta (la PWA no sufre regresión).
- **Q2 — Cliente de red Swift (B-02)**: A) núcleo auth-first (base URL, JSON, inyección de
  `Bearer`, errores tipados) + una llamada de humo a `/api/v1/user/me`.
- **Q3 — Estrategia de token**: A) access token en memoria + refresh token en iOS Keychain +
  refresh automático (auto-login silencioso al arrancar y refresh ante 401 con un reintento).
- **Q4 — Alcance del backend en F1**: A) ajuste aditivo completo de login/refresh/logout + sus
  tests dentro de este intent.
- **Q5 — Definición de hecho**: A) build + pytest verdes para el ajuste de backend + validación
  manual en el iPhone 13 Pro (login → refresh → logout); test de UI/dispositivo nativo queda
  como deuda registrada.
- **Q6 — Añadir/quitar del alcance**: None.

¿Está todo correcto?

[Answer]: Looks correct

