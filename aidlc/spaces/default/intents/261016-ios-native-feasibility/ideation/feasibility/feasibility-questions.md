# Feasibility & Constraints — Preguntas de clarificación

> Contexto ya decidido en intent-capture (no se re-pregunta): análisis iOS-only, uso
> personal, decisor único; Windows como única máquina (sin Mac) → `xtool` imprescindible;
> coste recurrente 0 € con firma gratuita refirmando cada ~7 días como ruta preferida y
> Apple Developer Program como excepción acotada a comparar; subconjunto núcleo = Login,
> Mercado, Presupuesto, Favoritos, Calculadora; backend FastAPI + Fly.io + Neon intacto.

## QF1. Framework de la app nativa: ¿qué tecnología asumimos como hipótesis principal del estudio?

El contexto del proyecto (reglas afirmadas) menciona NativeScript + Angular como ruta nativa, y `xtool` compila proyectos iOS "tipo SwiftPM". Importa fijar la hipótesis para enmarcar el análisis de portabilidad y de compatibilidad con `xtool`.

- A. NativeScript + Angular (`@nativescript/angular`): máxima reutilización de la lógica Angular existente (servicios, RxJS, signals); la UI se reescribe con componentes NativeScript. Es la hipótesis que sugieren las reglas del proyecto.
- B. Capacitor (envolver la PWA Angular actual en un WebView nativo): mínimo esfuerzo de UI pero sigue siendo web embebida, no "nativo real".
- C. Reescritura en Swift/SwiftUI nativo puro: máxima "natividad" pero descarta casi todo el código Angular; mayor esfuerzo.
- D. El estudio debe comparar explícitamente al menos dos de estas rutas y recomendar una.
- E. Not yet defined.
- X. Other (please specify)

[Answer]: C (ajustado). Swift/SwiftUI nativo puro, compilando/firmando/desplegando con `xtool`, como RUTA ÚNICA del estudio. El código Angular existente pasa a ser **especificación funcional de referencia** de las 5 pantallas núcleo, no código a migrar; lo único reutilizable es el backend FastAPI (intacto, por HTTP) y el conocimiento del dominio. Maximiza natividad y valor de aprendizaje (motivación B+C). NativeScript y Capacitor quedan descartados; se mencionan brevemente como alternativas no elegidas.

## QF2. Sobre `xtool` y su compatibilidad: ¿qué nivel de certeza tienes hoy sobre que soporta tu ruta?

`xtool` (xtool.sh) construye y firma apps iOS desde Linux/Windows usando el toolchain Swift open-source, pero funciona mejor con proyectos SwiftPM/Swift. Si la ruta es NativeScript (QF1=A), hay que validar si `xtool` puede empaquetar/firmar el `.ipa` que produce el build de NativeScript, o si sólo encaja con Swift nativo (QF1=C).

- A. No lo he probado aún; parte del estudio es determinar si `xtool` soporta mi ruta de framework elegida (riesgo técnico abierto a documentar en el RAID log).
- B. Ya he hecho una prueba básica con `xtool` y funciona para un proyecto de ejemplo; falta validarlo con mi stack real.
- C. Sé que `xtool` encaja con Swift nativo pero dudo de NativeScript; acepto que el estudio pueda concluir que la ruta de framework debe ajustarse a lo que `xtool` soporta.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: A. No probado aún; el estudio determina y documenta la cadena `xtool` end-to-end apoyándose en la documentación oficial (xtool.sh/documentation/xtool, consultada y verificada en esta etapa). Hallazgos confirmados de la doc: `xtool` es cross-platform (Linux/WSL/macOS), construye un paquete SwiftPM en app iOS, firma e instala apps iOS y habla con Apple Developer Services; en Windows funciona **vía WSL** (requiere Swift 6.4 toolchain + usbmuxd + USB passthrough del iPhone). Queda como riesgo abierto en el RAID log: validar el flujo completo con una app real (no sólo el ejemplo del tutorial).

## QF3. Firma gratuita y Apple ID: ¿qué tienes disponible para firmar/instalar en el iPhone?

La firma gratuita (free provisioning) requiere un Apple ID (sin pagar los 99 €) y tiene límites conocidos: certificado de desarrollo de 7 días, máximo ~3 apps firmadas gratis simultáneas por dispositivo, hasta 10 App IDs por 7 días, y ciertas capabilities (push, App Groups, iCloud...) no disponibles sin cuenta de pago.

- A. Tengo un Apple ID normal (gratuito) y el iPhone registrado en él; quiero exprimir la firma gratuita al máximo.
- B. Tengo Apple ID pero me preocupa el reconfirmado cada 7 días; el estudio debe proponer el flujo menos tedioso posible (p. ej. script de reinstalación desde Windows con `xtool`).
- C. Acepto que algunas capabilities nativas (push, widgets con ciertas capabilities) puedan quedar fuera del alcance si exigen cuenta de pago, y quiero que el estudio lo documente como límite.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: A. Tengo un Apple ID normal (gratuito) y el iPhone registrado en él; quiero exprimir la firma gratuita al máximo. Límites a documentar (confirmados por la doc oficial de `xtool`): certificado de desarrollo que caduca a ~7 días, `xtool` **prefija automáticamente el bundle ID** con cuentas gratuitas (p. ej. `XTL-1234.com.example.App`) porque dos cuentas no pueden compartir bundle ID; wildcard provisioning sólo con cuenta de pago; capabilities avanzadas limitadas sin Developer Program.

## QF3b. (derivada de la doc) ¿Cuál es tu situación con WSL?

La doc oficial de `xtool` indica que en Windows se usa **vía WSL** (no Windows nativo).

- A. Ya tengo WSL instalado y funcionando.
- B. No tengo WSL; entra como requisito previo a documentar.
- C. No sabía que requería WSL; recogerlo como prerrequisito.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: A. Ya tengo WSL instalado y funcionando en mi Windows. (Reduce el riesgo de entorno; el estudio asume WSL operativo y documenta Swift 6.4 toolchain + usbmuxd + USB passthrough como requisitos de la cadena.)

## QF4. Reutilización del backend y contrato de API: ¿la app nativa consume la misma API que la PWA sin cambios?

El backend FastAPI + Fly.io + Neon queda fuera de alcance (intacto). Pero la PWA usa auth con access token en memoria + refresh token en cookie HttpOnly. Una app nativa no tiene cookies de navegador: el refresh token tendría que ir a almacenamiento seguro nativo (iOS Keychain), según las reglas del proyecto.

- A. Sí, la app nativa consume la misma API `/api/v1/*` y `/auth/*` sin cambios en el backend; el único ajuste es cómo el cliente nativo guarda/envía los tokens (Keychain en vez de cookie), que es trabajo de cliente, no de backend.
- B. Igual que A, pero quiero que el estudio evalúe si el flujo de refresh basado en cookie HttpOnly obliga a algún ajuste mínimo del backend (p. ej. aceptar el refresh token por header/body además de cookie) y lo documente como riesgo/dependencia.
- C. Not yet defined — depende del análisis del cliente de auth.
- X. Other (please specify)

[Answer]: B. La app nativa Swift consume la misma API `/api/v1/*` y `/auth/*`; el cliente Swift guarda el refresh token en el **iOS Keychain** (NUNCA en claro, regla durable del proyecto). El estudio DEBE evaluar si el flujo de refresh basado en cookie `HttpOnly` obliga a un ajuste mínimo del backend (p. ej. aceptar el refresh token por header/body además de cookie, ya que un cliente nativo no gestiona cookies de navegador como lo hace Angular) y documentarlo como **dependencia/riesgo** — sin tocar el backend en este intent de análisis.

## QF5. Restricciones de tiempo/esfuerzo: ¿hay algún límite que deba condicionar la recomendación?

Para calibrar el go/no-go y la agresividad de la ruta por fases.

- A. Sin plazo; es un proyecto personal y el tiempo lo pongo yo a ratos. El estudio debe optimizar por esfuerzo total razonable, no por fecha.
- B. Quiero algo usable en pocas semanas de trabajo intermitente; prioriza la ruta más corta aunque sacrifique "natividad".
- C. El aprendizaje importa tanto como el resultado; acepto una ruta más larga si enseña más (coherente con la motivación de ejercicio técnico).
- D. Not applicable / Not yet defined.
- X. Other (please specify)

[Answer]: A. Sin plazo; proyecto personal, tiempo a ratos. El estudio optimiza por esfuerzo total razonable, no por fecha. (Coherente con QF1=C y la motivación de ejercicio técnico: se prioriza natividad y aprendizaje sobre rapidez.)

<!-- Nota: puedes responder en modo Guía (una a una), Edición (rellenas los [Answer]:), o Chat (lenguaje natural y yo relleno). -->
