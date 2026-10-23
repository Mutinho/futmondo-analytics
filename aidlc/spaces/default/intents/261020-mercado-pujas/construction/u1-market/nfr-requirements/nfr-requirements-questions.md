# NFR Requirements — Preguntas (u1-market)

> Unit `u1-market` (kind `ui`). Los NFR ya están acotados por los requisitos
> (NFR1–NFR6) y por la capa nativa existente de F1/F2. Al ser `ui`, esta Unit
> produce `performance-requirements.md`, `security-requirements.md`,
> `tech-stack-decisions.md` y `traceability.json` (scalability/reliability/
> observability son de kind `service`, NO aplican aquí: el backend es inalterado).

## Q1 — Objetivo de rendimiento de la UI

- A. **Objetivos de responsividad de UI, no SLAs de servidor**: la pantalla
  renderiza el primer frame de estado (loading) de inmediato al aparecer; la
  lista se muestra en cuanto resuelve `/market/today`; el scroll de la lista es
  fluido (LazyVStack); el reordenado es instantáneo (opera sobre la lista en
  memoria, sin red). No se fijan SLAs de latencia de red (dependen del backend
  inalterado y de la conexión del dispositivo). Sin métricas de throughput de
  servidor (no es un servicio). (Traza: NFR latencia percibida; alineado con F2.)
- B. Otro (especificar).

[Answer]: A

## Q2 — Seguridad de la pantalla (incl. la novedad: escritura)

- A. **Reforzar las garantías ya afirmadas, sin nada nuevo**: toda llamada
  (`/market/today`, `/market/bid`, `/market/cancelbid`, `/sofascore/player`) viaja
  con `Authorization: Bearer <access token>` en memoria; el refresh token sólo en
  Keychain (`AfterFirstUnlockThisDeviceOnly`); ningún material de credencial
  (password/token) aparece en logs, `repr`, `exc_info` ni en los avisos de error
  de puja/cancelación (los avisos usan el `message`/`detail` del backend o un
  texto genérico). Las escrituras son endpoints autenticados; el backend es
  autoridad de validación (`price>0`, `price≤5e9`). TLS obligatorio (base URL
  https; `NetworkClient` rechaza no-https, SEC-N1). (Traza: NFR3.)
- B. Otro (especificar).

[Answer]: A

## Q3 — Decisiones de tech stack

- A. **Sin tecnología nueva**: SwiftUI + Foundation/`URLSession` + Observation +
  Security/Keychain + XCTest, todo SDK de Apple; `Package.swift` sigue con
  `dependencies: []`. Se reutilizan `FutmondoKit` (NetworkClient, AuthService,
  DesignSystem) y `FutmondoApp` (componentes) de F1/F2. Coste 0 €. (Traza: NFR1.)
- B. Otro (especificar).

[Answer]: A

## Q4 — Accesibilidad e idioma (NFR4, NFR6)

- A. **Mantener lo afirmado**: identificadores/comentarios en inglés, texto de
  usuario en castellano; significado no sólo por color (flecha+signo en
  tendencia, etiqueta+color en Balance/Disponible, icono+texto en errores);
  etiquetas accesibles y operable con VoiceOver; contraste WCAG AA vía
  `ContrastRatio`; áreas táctiles ≥44pt. (Traza: NFR4, NFR6.)
- B. Otro (especificar).

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Resumen NFR de `u1-market` antes de generar los artefactos:

- **Rendimiento (NFR latencia percibida)**: objetivos de responsividad de UI
  (primer frame de estado inmediato, lista al resolver `/market/today`, scroll
  fluido con LazyVStack, reordenado instantáneo en memoria); sin SLAs de servidor.
- **Seguridad (NFR3)**: Bearer en memoria + refresh en Keychain
  (`AfterFirstUnlockThisDeviceOnly`); sin material de credencial en logs/`repr`/
  `exc_info`/avisos; escrituras autenticadas con el backend como autoridad de
  validación (`price>0`, `price≤5e9`); TLS obligatorio (NetworkClient rechaza
  no-https).
- **Tech stack (NFR1)**: sin tecnología nueva — SwiftUI + Foundation/URLSession +
  Observation + Security/Keychain + XCTest (SDK de Apple); `dependencies: []`;
  reutiliza FutmondoKit/FutmondoApp. Coste 0 €.
- **Accesibilidad/idioma (NFR4, NFR6)**: inglés en código / castellano en UI;
  significado no sólo por color; VoiceOver; WCAG AA (ContrastRatio); táctil ≥44pt.
- **Artefactos a generar**: `performance-requirements.md`,
  `security-requirements.md`, `tech-stack-decisions.md`, `traceability.json`.
  (Unit `ui`: NO scalability/reliability/observability — son de kind `service`.)

¿Todo correcto antes de generar los artefactos?

- **Looks correct** — confirmo y genero.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
