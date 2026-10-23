# User Stories — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, VoiceOver, Material 3) verbatim en inglés.
> Formato INVEST; AC en Given/When/Then; IDs `US{grupo}.{seq}` / `AC{grupo}.{seq}.{n}`. Persona única: propietario/mantenedor-usuario.

## Grupo 1 — Tokens (color, tipografía, espaciado)

### US1.1 — Tokens de color claro/oscuro
Como mantenedor, quiero tokens de color semánticos que reproduzcan los roles clave del tema de Angular en claro y oscuro, para que todas las pantallas usen los mismos colores sin definirlos a mano. (Must) [FR1]
- **AC1.1.1** Dado el sistema de diseño, cuando consulto los tokens, entonces existen `primary` (verde), `tertiary` (violeta), `surface`/`on-surface` y variantes, más `money-positive`/`money-negative` y el gradiente de splash. [FR1.1][FR1.2][FR1.3]
- **AC1.1.2** Dado un dispositivo en modo oscuro, cuando se resuelve un token de color, entonces devuelve su variante oscura automáticamente; en modo claro, la clara. [FR1.4]

### US1.2 — Tipografía con Dynamic Type
Como usuario, quiero una escala tipográfica `h1/h2/h3` + body basada en Roboto que escale con Dynamic Type, para leer cómodamente al ajustar el tamaño de texto del sistema. (Must) [FR2]
- **AC1.2.1** Dado el sistema de diseño, cuando consulto la tipografía, entonces existe una escala `h1`/`h2`/`h3` + body basada en Roboto. [FR2.1]
- **AC1.2.2** Dado un estilo tipográfico del sistema, cuando aumento el tamaño de texto del sistema, entonces el texto escala (Dynamic Type). [FR2.2]
- **AC1.2.3** Dado que Roboto no está empaquetada, cuando se renderiza, entonces se usa la fuente del sistema con la misma escala (fallback). [FR2.3]

### US1.3 — Escala de espaciado
Como mantenedor, quiero una escala de espaciado reutilizable, para componer layouts consistentes. (Must) [FR3]
- **AC1.3.1** Dado el sistema, cuando uso el espaciado, entonces dispongo de pasos fijos `xs/sm/md/lg/xl` consumidos por los componentes. [FR3.1]

## Grupo 2 — Componentes base

### US2.1 — Componentes base con estados
Como mantenedor, quiero botón, campo de texto, tarjeta y estados de carga/error como componentes SwiftUI que consuman los tokens, para construir pantallas sin estilos ad-hoc. (Must) [FR4]
- **AC2.1.1** Dado el botón primario, cuando está normal/disabled/loading, entonces refleja cada estado visual correctamente. [FR4.1]
- **AC2.1.2** Dado el campo de texto, cuando tiene label, icono opcional y error, entonces los muestra según el estado. [FR4.2]
- **AC2.1.3** Dada la tarjeta, cuando se usa como superficie, entonces aplica los tokens de surface. [FR4.3]
- **AC2.1.4** Dados los estados de carga/error, cuando se usan, entonces son reutilizables y consistentes. [FR4.4]
- **AC2.1.5** Dado cualquier componente, cuando cambia el modo claro/oscuro, entonces responde sin estilos ad-hoc por pantalla. [FR4.5][FR1.4]
- **AC2.1.6** (Accesibilidad) Dado un componente, cuando VoiceOver está activo, entonces expone etiqueta/rol correctos; y su contraste cumple ≥4.5:1 (texto normal) / ≥3:1 (texto grande y UI) en claro y oscuro. [NFR1]
- **AC2.1.7** (Accesibilidad) Dado un componente con texto, cuando cambia el tamaño de Dynamic Type del sistema, entonces su texto escala sin recortes ni solapamientos. [NFR1][FR2.2]

## Grupo 3 — Catálogo/preview

### US3.1 — Catálogo verificable
Como mantenedor, quiero una pantalla de catálogo que muestre tokens y componentes con toggles de claro/oscuro y tamaño de texto, para verificar de un vistazo la fidelidad contra el tema de Angular. (Must) [FR5]
- **AC3.1.1** Dado el catálogo, cuando lo abro, entonces muestra todos los tokens (colores, tipografía, espaciado) y todos los componentes base. [FR5.1]
- **AC3.1.2** Dado el catálogo, cuando alterno claro/oscuro y cambio el tamaño de Dynamic Type, entonces los componentes se actualizan y permiten comparar con el tema de Angular. [FR5.2][NFR3]

## Grupo 4 — Revestir F1

### US4.1 — Login revestido sin regresión
Como usuario, quiero que el login de F1 se vea con el nuevo sistema de diseño sin que cambie su comportamiento, para tener coherencia visual sin perder funcionalidad. (Must) [FR6]
- **AC4.1.1** Dado el login revestido, cuando introduzco credenciales válidas, entonces los flujos de F1 funcionan igual: (1) login con email/contraseña → sesión; (2) auto-login silencioso al arrancar recuperando el refresh token del Keychain; (3) refresh del access token ante 401 con un reintento; (4) logout que revoca la sesión. [FR6.2]
- **AC4.1.2** Dado el login revestido, cuando hay un error o validación, entonces se muestran con los componentes del sistema sin cambiar la lógica. [FR6.1][FR4.2][FR4.4]
- **AC4.1.3** Dado el iPhone 13 Pro, cuando verifico manualmente, entonces no hay regresión funcional respecto a F1. [FR6.2]

## Notas INVEST

Historias independientes por área, negociables, valiosas (cada una entrega parte del sistema), estimables, pequeñas y testables (AC verificables manualmente en el iPhone 13 Pro; accesibilidad con Accessibility Inspector). El arnés de test de UI nativo automatizado queda fuera (diferido). [team-practices]

## Assumptions & Open Questions

None.
