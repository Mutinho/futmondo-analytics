# Intent Capture — Preguntas de clarificación

## Sources

- [desc] Initial description: "--description Análisis y planificación para, partiendo del código Angular existente, crear una aplicación nativa iOS; usar la herramienta xtool (https://xtool.sh/) para poder compilar en Windows. Evaluar viabilidad incluyendo el mandato de coste 0€ frente al coste anual del Apple Developer Program, explorando la instalación en dispositivo con firma gratuita (que caduca cada pocos días)."
- [scope] Workflow-selected scope: `bugfix`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Mandated`: "ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); descartar toda mejora o dependencia con gasto recurrente. **Excepción aceptada y acotada**: el **coste de publicación de distribución nativa** (Apple Developer Program ~99 €/año; Google Play Developer) es una excepción conocida y bounded a este mandato, exclusivamente para habilitar la distribución de una app nativa; el análisis de viabilidad lo documenta como coste recurrente de distribución."
- [memory:M2] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de datos); cualquier modelo de sesión que proponga el análisis nativo debe preservar esta garantía. Al perder la cookie `HttpOnly` del navegador, el refresh token debe ir a **almacenamiento seguro nativo** (iOS Keychain / Android Keystore vía `@nativescript/secure-storage`), **NUNCA** a `ApplicationSettings` ni `localStorage` en claro."
- [memory:M3] `aidlc/spaces/default/memory/team.md#Testing Posture`: "la suite frontend actual (15 `*.spec.ts` sobre `@angular/build:unit-test`, builder Vitest `4.1.11` + `@vitest/coverage-v8` + `jsdom`) **no porta tal cual** a NativeScript: no hay DOM/`jsdom`, el runner Angular CLI de Vitest no aplica y los specs que montan componentes Material/CDK no portan; los specs de servicios/RxJS/signals son portables casi 1:1."

---

## Q1. ¿Cuál es el problema de negocio / motivación personal que resuelve pasar de la PWA Angular a una app nativa iOS?

La descripción pide analizar y planificar una app nativa iOS partiendo del código Angular existente, pero no dice qué duele hoy de la PWA. Ayuda a enmarcar el estudio saber el "para qué".

- A. La PWA en iOS Safari tiene limitaciones molestas (instalación/engagement, notificaciones push, iconos/splash, comportamiento en segundo plano) que una app nativa resolvería.
- B. Se busca una experiencia más "app" (menú inferior iOS, gestos, widgets de pantalla de inicio) que la PWA no da bien.
- C. Es principalmente un ejercicio técnico / de aprendizaje (probar NativeScript + xtool, compilar iOS desde Windows) sin un dolor funcional concreto.
- D. Rendimiento/arranque: la PWA se siente lenta o pesada en el iPhone y se quiere mejorar.
- E. Not yet defined — el estudio de viabilidad debe ayudar a decidir si merece la pena.
- X. Other (please specify)

[Answer]: B + C. Se busca una experiencia más "app" nativa (menú inferior iOS, gestos, widgets) y a la vez es un ejercicio técnico/de aprendizaje con NativeScript + xtool y compilar iOS desde Windows.

## Q2. ¿Quién es el usuario de la app nativa y en qué dispositivos debe funcionar?

El contexto del proyecto menciona iPhone 13 Pro y Samsung A17. Importa saber el alcance de plataformas para dimensionar el análisis (iOS-only vs. iOS+Android).

- A. Uso personal del propietario; sólo iPhone (iOS) es el objetivo de este estudio.
- B. Uso personal pero multi-dispositivo: iOS (iPhone 13 Pro) **y** Android (Samsung A17); el estudio debe cubrir ambos aunque la descripción enfatice iOS.
- C. Pequeño grupo privado de amigos/liga (varios usuarios Futmondo), iOS prioritario.
- D. Distribución pública más amplia (App Store para cualquiera).
- E. Not yet defined.
- X. Other (please specify)

[Answer]: A. Uso personal del propietario; sólo iPhone (iOS) es el objetivo de este estudio.

## Q3. ¿Cómo es el "éxito" de este análisis de viabilidad? ¿Qué debe permitirte decidir?

Es un intent de análisis: el entregable es un documento de viabilidad + ruta de implementación, no la app. Conviene fijar qué decisión habilita.

- A. Un go/no-go claro sobre migrar a nativo con NativeScript, con esfuerzo estimado y riesgos de portabilidad del código Angular existente.
- B. Confirmar que el flujo técnico es viable a coste recurrente 0 €: compilar iOS en Windows con xtool y poder instalar en el iPhone con firma gratuita (refirmando cada ~7 días), evitando el Apple Developer Program.
- C. Comparar explícitamente las dos rutas de distribución (firma gratuita que caduca vs. Apple Developer Program ~99 €/año) con sus pros/contras y recomendación.
- D. Una ruta de implementación por fases (qué se reutiliza del backend/Angular, qué se reescribe, en qué orden) lista para abrir un intent de construcción después.
- E. Todas las anteriores (A+B+C+D).
- X. Other (please specify)

[Answer]: E. Todas las anteriores (A+B+C+D): go/no-go con riesgos de portabilidad, viabilidad técnica del flujo coste 0 € (xtool en Windows + firma gratuita refirmando cada ~7 días), comparativa de distribución (firma gratuita vs. Apple Developer Program) y ruta de implementación por fases. La ruta por fases (D) se mantiene a nivel de fases y bloques reutilizables, sin detalle de implementación fino (que queda para un intent de construcción posterior).

## Q4. Sobre xtool y la compilación de iOS en Windows: ¿cuál es la restricción real de tu entorno?

xtool compila/firma apps iOS sin Xcode/macOS. Entender tu entorno acota qué hay que probar y documentar.

- A. No tengo Mac en absoluto; Windows es mi única máquina y xtool (o equivalente) es imprescindible para que esto sea viable.
- B. Tengo Windows principalmente, pero tengo acceso ocasional a un Mac (prestado/CI) como alternativa si xtool no basta.
- C. Me interesa xtool por preferencia/coste, pero el bloqueante duro es el coste 0 €, no el sistema operativo.
- D. Not yet defined — parte del estudio es ver qué exige realmente xtool.
- X. Other (please specify)

[Answer]: A. No tengo Mac en absoluto; Windows es mi única máquina y xtool (o equivalente) es imprescindible para que esto sea viable.

## Q5. Sobre el coste 0 € y la firma gratuita que caduca cada pocos días: ¿qué nivel de fricción estás dispuesto a aceptar?

La firma gratuita de Apple (free provisioning) caduca a los ~7 días: la app deja de abrir y hay que reinstalar/refirmar. El Apple Developer Program (~99 €/año) evita eso. Esto es el núcleo del trade-off a analizar.

- A. Acepto reinstalar/refirmar cada ~7 días con tal de mantener coste recurrente 0 €; es la ruta preferida y el estudio debe optimizar ese flujo.
- B. Prefiero coste 0 € pero quiero que el estudio evalúe honestamente si la fricción de refirmar es asumible a largo plazo antes de descartar el Apple Developer Program.
- C. Estoy abierto a pagar el Apple Developer Program (excepción de coste de distribución ya contemplada en las reglas del proyecto) si la firma gratuita resulta demasiado molesta; quiero la comparativa para decidir.
- D. Not yet defined — depende de lo que concluya el análisis.
- X. Other (please specify)

[Answer]: A. Acepto reinstalar/refirmar cada ~7 días con tal de mantener coste recurrente 0 €; es la ruta preferida y el estudio debe optimizar ese flujo.

## Q6. Alcance funcional de la app nativa en esta primera versión: ¿paridad total con la PWA o un subconjunto?

La PWA actual tiene muchas pantallas (Presupuesto, Mercado, Sync, Finanzas, Evolución, Estadísticas, Clausulables, Analytics, Dark Mode, PWA install). Conviene saber qué debe cubrir el análisis como objetivo de portabilidad.

- A. Paridad funcional completa con la PWA actual (todas las pantallas y features).
- B. Un subconjunto núcleo (p. ej. login + Mercado + Finanzas + Sync) como primera versión nativa, dejando el resto para después.
- C. El estudio debe recomendar el subconjunto mínimo viable para la primera app nativa, no lo fijo yo.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: B. Un subconjunto núcleo como primera versión nativa: Login, Mercado, Presupuesto, Favoritos y Calculadora; el resto de pantallas queda para después. (Nota: "Favoritos" y "Calculadora" se mapearán contra el código Angular real en reverse-engineering; "Calculadora" probablemente corresponde a Finanzas y "Favoritos" a jugadores marcados, a confirmar.)

## Q7. ¿Quién decide el alcance y las prioridades de este trabajo, y hay algún stakeholder más allá de ti?

Para el mapa de stakeholders. En un proyecto personal lo normal es un único decisor.

- A. Yo soy el único stakeholder y decisor (proyecto personal).
- B. Yo decido, pero hay otros usuarios (amigos/liga) cuya experiencia debo tener en cuenta como influenciadores.
- C. Hay un tercero cuyo visto bueno necesito (p. ej. coste del Apple Developer Program).
- D. Not identified.
- X. Other (please specify)

[Answer]: A. Yo soy el único stakeholder y decisor (proyecto personal).

## Q8. ¿Qué debe quedar explícitamente FUERA de este primer análisis de viabilidad?

El scope del workflow (`bugfix`) ya está elegido; esta pregunta es sobre los límites del producto/estudio, no sobre el scope del workflow. Marca lo que NO quieres que este análisis aborde.

- A. Fuera: la publicación en App Store para terceros (distribución pública masiva); el estudio se centra en instalación personal/privada.
- B. Fuera: Android/NativeScript-Android; el estudio es iOS-only aunque exista un Samsung A17.
- C. Fuera: cualquier cambio en el backend FastAPI o la infraestructura Fly.io/Neon (el análisis asume el backend intacto).
- D. Fuera: rediseño de UX/UI; se analiza portabilidad del diseño actual, no un rediseño.
- E. None — quiero que el análisis sea lo más abarcador posible dentro de la viabilidad.
- X. Other (please specify)

[Answer]: A + B + C. Fuera: publicación en App Store para terceros (distribución pública masiva); Android/NativeScript-Android (iOS-only); y cualquier cambio en el backend FastAPI o la infraestructura Fly.io/Neon (se asume el backend intacto). La UI/UX NO se excluye: el rediseño necesario al portar a controles nativos (menú inferior iOS, componentes nativos) se trata DENTRO del análisis como portabilidad de UI, no como rediseño visual desde cero.

<!-- Nota: puedes responder en modo Guía (te pregunto una a una), Edición (rellenas tú los [Answer]: en este fichero), o Chat (me respondes en lenguaje natural y yo relleno). -->

## Assumption Confirmation

Los artefactos recogen estos supuestos (marcados `[assumption]`). Elige cómo proceder:

Supuestos:
1. "Favoritos" y "Calculadora" (del subconjunto núcleo) no aparecen literalmente en el README; se asume Calculadora ≈ Finanzas y Favoritos ≈ jugadores marcados, a confirmar contra el código Angular real en reverse-engineering.
2. Se asume que la firma gratuita de Apple caduca a ~7 días y obliga a reinstalar/refirmar; el valor exacto y el flujo se verificarán en feasibility.
3. Se asume que `xtool` permite compilar y firmar iOS desde Windows sin Mac; su alcance real, requisitos y límites son objeto del estudio de feasibility.
4. Al ser proyecto personal con decisor único, no hay requisitos formales de comunicación ni cadencia de reporte más allá de los gates del workflow.

Opciones:
- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A. Accept assumptions
