# Prácticas NUEVAS o específicas de F1 — PROPUESTAS a afirmar

> Etapa: inception (practices-discovery). Intent: `261016-f1-login-nativo`.
> Idioma: castellano; tokens técnicos verbatim en inglés.
>
> **Estado de todo este fichero**: cada regla de abajo es una **PROPUESTA a
> afirmar**, NO una práctica ya vigente. Hoy ninguna está en `team.md` ni
> `project.md`; cubren el hueco que abre F1 (primer cliente **nativo iOS Swift**,
> superficie que no existía cuando se afirmaron las prácticas actuales). La
> afirmación es un paso human-gated posterior; este fichero no edita `memory/`.
>
> Las reglas durables ya vigentes (coste 0 €, gate de CI, trunk-based,
> seguridad de credenciales, testing posture backend/frontend, no ampliar
> god-files) están reconocidas en `team-practices.md` y **no** se re-proponen
> aquí. Lo de abajo es especialización aditiva, nunca contradicción (si algo
> contradijera una regla más amplia, sería un error de admisión, no un override).

---

## PROPUESTA P-1 — Testing posture del cliente nativo Swift (asimétrica respecto al backend)

**PROPUESTA a afirmar.** Reconociendo que la testing posture afirmada
(test-after + aserción de efecto + fakes in-memory + ratchet) se midió sobre
`pytest` (backend) y `Vitest` (frontend Angular), y que **hoy no existe arnés de
test iOS** (ni XCTest, ni runner de dispositivo), se propone para F1:

- La **verificación del cliente nativo Swift en F1 es MANUAL**, documentada en el
  **iPhone 13 Pro** (recorrido login → refresh automático → logout), tal como fija
  la Definición de Hecho del scope. No se introduce piso de cobertura iOS en F1.
- El **arnés XCTest (unit + UI/dispositivo) queda como DEUDA REGISTRADA**
  explícita, a abordar en un intent posterior (p. ej. F2/F3), no en F1. No es una
  excepción silenciosa: se registra como deuda, igual que ESLint frontend o el
  arnés de test nativo citados como deuda diferida en el proyecto.
- Cuando el arnés iOS se cree, su umbral de cobertura es un **suelo nuevo bajo
  tooling distinto** (XCTest), **no un trinquete que arrastre** el piso de
  `pytest`/`Vitest`. El ratchet por-runner sólo sube dentro de su propio runner.
  (Coherente con la nota de portabilidad ya afirmada en `team.md` Testing Posture
  sobre re-basar cobertura en un runner distinto.)
- La posture **test-after con aserción de efecto** sí se **adopta como intención
  durable** para el futuro código Swift testeable (cuando haya arnés), espejando
  la del backend/frontend; en F1 sólo se difiere su *enforcement* automático.

*Por qué es nueva*: las reglas de ratchet y fakes in-memory vigentes no dicen
nada sobre un runner iOS inexistente; esto rellena ese silencio sin tocar el piso
backend/frontend.

---

## PROPUESTA P-2 — Ajuste de backend D-01 estrictamente ADITIVO, cubierto por `pytest`, sin romper el canal cookie de la PWA

**PROPUESTA a afirmar.** Para el ajuste del transporte del refresh token (D-01):

- El cambio es **estrictamente aditivo**: `/auth/login` devuelve el refresh token
  **también** en el body; `/auth/refresh` y `/auth/logout` **aceptan** el refresh
  token por body/header; el canal cookie `HttpOnly` (`futmondo_refresh_token`,
  `path="/auth"`, `samesite=lax`) de la PWA **se preserva sin regresión**
  (C-03, R-01).
- Se exigen **tests `pytest` que aseveran el efecto en AMBOS canales**: refresh
  por cookie (comportamiento PWA actual) **y** refresh por body/header
  (comportamiento del cliente nativo), incluyendo el borrado/revocación en
  `logout` por ambas vías. Nada de `pytest.raises` sin aserción de estado.
- **characterization-first**: antes de tocar `auth/routes.py`/`jwt_utils.py`, la
  red existente (`test_auth_characterization.py`, `test_jwt_startup.py`,
  `test_token_store_migrations.py`) debe quedar verde; los nuevos tests se añaden,
  no se reescriben los god-files ni el SQL-en-router de `auth/routes.py`.
- El transporte del refresh por body/header **NO introduce secretos nuevos** ni
  cambia la criptografía (sigue PyJWT HS256, mismo `JWT_SECRET` fail-fast); sólo
  cambia el canal de transporte.
- **No se altera la whitelist de CORS por un origen nativo**: D-01 (refresh fuera
  de cookie) evita precisamente la dependencia CORS+cookies para el cliente
  nativo; cualquier ampliación de CORS queda fuera de alcance.

*Por qué es nueva*: la regla de "ajuste aditivo que preserva el canal cookie" y
la de "cubrir ambos canales con `pytest`" son específicas de D-01; las reglas
vigentes de testing/brownfield las respaldan pero no las enuncian.

---

## PROPUESTA P-3 — Dependencias nativas: SOLO SDK de Apple, cero librerías de terceros (coherente con coste 0 €)

**PROPUESTA a afirmar.** Para el cliente nativo iOS de F1:

- El cliente usa **exclusivamente SDK de Apple**: `URLSession` (red),
  **Keychain Services** (almacén seguro del refresh token), `SwiftUI` + APIs
  nativas de UX (`matchedGeometryEffect`, `symbolEffect`, `@FocusState`,
  `.sensoryFeedback`, `.ultraThinMaterial`, `.textContentType`), y
  `LocalAuthentication` **sólo si/cuando** se active Face ID / Touch ID (hoy
  **diferido** como fast-follow, fuera de F1).
- **CERO librerías de terceros** (sin Alamofire, sin KeychainAccess, sin SPM
  packages externos) en F1. Si en el futuro se propusiera alguna, sería **OSS,
  fijada a versión exacta** vía SPM, y requeriría afirmación explícita; no se
  prevé ninguna porque el SDK de Apple es suficiente.
- Esta regla es **especialización** del mandato durable de coste 0 € / "sin
  dependencias de pago, OSS pin exacto", aplicado a la superficie nativa; no lo
  relaja. La **excepción acotada** ya afirmada (Apple Developer Program ~99 €/año
  para distribución) se mantiene tal cual y no se amplía.

*Por qué es nueva*: las reglas vigentes hablan de dependencias Python/npm; no
existe hoy una regla sobre dependencias Swift/SPM del cliente nativo.

---

## PROPUESTA P-4 — Convenciones de scope de commit e idioma para la superficie Swift

**PROPUESTA a afirmar.** Especialización menor de las convenciones vigentes para
el nuevo árbol de código nativo:

- Scope de **Conventional Commits** para la app iOS: un scope estable (p. ej.
  `feat(ios-auth)`, `feat(ios-net)`), en castellano el cuerpo/descripción, igual
  que el resto del repo.
- **Identificadores, tipos, propiedades y comentarios Swift en inglés**; **textos
  visibles del login** (labels, mensajes de error de UI) y **mensajes de commit**
  en **castellano**, extendiendo C-04 a Swift/SwiftUI sin cambiarlo.

*Por qué es nueva*: sólo precisa cómo aterriza la regla de idioma/commits ya
vigente en el nuevo stack Swift; es aditiva y no contradice nada.

---

## Nota de admisión

Ninguna propuesta baja un umbral, relaja el gate de CI, amplía god-files, ni
introduce coste recurrente nuevo (más allá de la excepción de distribución ya
afirmada). Todas son estrictamente aditivas sobre el chain `org → team →
project`. La decisión de afirmarlas (y en qué layer) es del humano en el gate de
afirmación posterior.

## Sources

- `aidlc/spaces/default/intents/261016-f1-login-nativo/ideation/scope-definition/scope-document.md`
  (dentro/fuera de alcance, Definición de Hecho, deuda del arnés iOS, polish
  SwiftUI sin dependencias externas).
- `aidlc/spaces/default/intents/261016-f1-login-nativo/ideation/feasibility/constraint-register.md`
  (C-01 coste 0 €/SDK; C-02 Keychain; C-03 aditivo/cookie; C-04 idioma;
  C-05 gate; C-06 secretos; C-07 `xtool`).
- `aidlc/spaces/default/intents/261016-f1-login-nativo/ideation/feasibility/raid-log.md`
  (R-01 regresión cookie; R-02 Keychain; R-03 divergencia refresh; D-01 aditivo).
- `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md` (modelo de
  auth: refresh sólo por cookie `HttpOnly` hoy; CORS+cookies; D-01 evita CORS).
- `aidlc/spaces/default/codekb/futmondo-analytics/code-quality-assessment.md`
  (red de tests de auth; ESLint/arnés nativo como deuda diferida; ratchet).
- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md` /
  `dependencies.md` (stack sin dependencias de pago; `xtool`; Keychain nativo).
- `aidlc/spaces/default/memory/team.md`, `project.md` (reglas durables que estas
  propuestas especializan sin contradecir).

## Assumptions & Open Questions

- **A-01 (abierta)**: el **cómo exacto** del transporte del refresh token
  (body vs. header, nombre del campo) es decisión de diseño de F1 (A-03 del RAID);
  P-2 fija el principio (aditivo + ambos canales con `pytest`), no la firma
  concreta.
- **A-02 (abierta)**: si P-1/P-3/P-4 deben afirmarse en `team.md` (durable para
  todo futuro código nativo) o en `project.md` (específico de este proyecto) es
  decisión del gate de afirmación humano; la recomendación es `project.md` para la
  posture iOS deferida (P-1) y las convenciones de scope (P-4), y `team.md` para
  el principio aditivo de backend (P-2) y la regla de dependencias nativas (P-3),
  por su carácter durable.
