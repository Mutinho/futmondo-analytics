# Feasibility Assessment — App nativa iOS (Swift) desde Angular, build con xtool en Windows/WSL

> Fase: ideación. Entregable de análisis (prosa), no código. Estimaciones conservadas y
> supuestos marcados conforme a los guardarraíles de ideación. Fuentes: intent-statement,
> respuestas `[QF<n>]`, documentación oficial de `xtool` consultada
> (`xtool.sh/documentation/xtool`), y una exploración ligera del frontend Angular existente.

## 1. Resumen ejecutivo (go/no-go preliminar)

**Veredicto preliminar: GO condicionado**, con un hito de validación temprana obligatorio
(spike de la cadena `xtool` end-to-end). La ruta elegida —Swift/SwiftUI nativo puro,
construido, firmado e instalado con `xtool` desde Windows vía WSL, a coste recurrente 0 €
con firma gratuita— es **técnicamente plausible** según la documentación oficial de `xtool`
y el estado del proyecto, pero su viabilidad depende de un riesgo que hoy no está validado
en vivo: que la cadena completa (build Swift → firma con cuenta gratuita → instalación en el
iPhone 13 Pro) funcione end-to-end en tu entorno. [QF1] [QF2] [desc]

El coste de equivocarse es bajo (es un proyecto personal sin plazo [QF5], y la decisión es
reversible: si `xtool`+firma gratuita no cuaja, se puede reconsiderar el Apple Developer
Program o la ruta de framework), por lo que el GO condicionado es prudente.

## 2. Ruta técnica elegida

Swift/SwiftUI **nativo puro** como ruta única del estudio. [QF1]

- **Reutilizable**: el backend FastAPI (`/api/v1/*`, `/auth/*`), consumido por HTTP, queda
  **intacto** [QF4]; y el **conocimiento de dominio** (modelos, fórmulas de finanzas, flujos
  de las pantallas). [QF1]
- **Se reescribe**: todo el cliente (UI en SwiftUI, capa de red, modelos, estado) desde cero
  en Swift. El código Angular/TypeScript existente actúa como **especificación funcional de
  referencia**, no como código a portar. [QF1]
- **Alternativas descartadas** (mencionadas para trazabilidad, no analizadas en profundidad):
  NativeScript+Angular (más reutilización de lógica pero menos natividad y peor encaje con
  `xtool`), y Capacitor (WebView, no "nativo real"). [QF1]

## 3. Cadena de build/firma/deploy con xtool (viabilidad técnica)

Hechos verificados en la documentación oficial de `xtool` (`xtool.sh/documentation/xtool`,
consultada en esta etapa): [QF2]

- `xtool` es un reemplazo de Xcode cross-platform (Linux/WSL/macOS) basado en estándares
  abiertos: **construye un paquete SwiftPM en una app iOS, firma e instala apps iOS**, e
  interactúa con Apple Developer Services. [QF2]
- **En Windows se usa vía WSL** (no Windows nativo). Prerrequisitos: WSL con USB passthrough
  para enlazar el iPhone, **Swift 6.4 toolchain**, y **usbmuxd** (libimobiledevice) para
  hablar con el dispositivo. [QF2] [QF3b]
- Configuración del proyecto vía **`xtool.yml`** (`version`, `bundleID`, `product`,
  `extensions`); `xtool new` genera la plantilla; `xtool dev [build]` construye y permite
  inspeccionar el `.app`. [QF2]
- **Widgets** y otras App Extensions son posibles declarando un producto adicional en
  `Package.swift` + entrada `extensions` en `xtool.yml` + `Info.plist` de la extensión. [QF2]

Estado en tu entorno: **WSL ya instalado y operativo** [QF3b], lo que reduce el riesgo de
setup. La cadena **no está aún validada en vivo** con una app real [QF2] → ver RAID
(R-01).

## 4. Firma gratuita y coste 0 € (análisis del trade-off central)

Con un Apple ID gratuito (sin Apple Developer Program) y `xtool`: [QF3] [memory:M1]

- **Caducidad ~7 días**: el certificado/provisioning de desarrollo gratuito expira a los
  ~7 días; la app deja de abrir y hay que reinstalar/refirmar. Asumido y aceptado como coste
  de fricción a cambio de 0 € recurrente. [QF3] [desc]
- **Prefijo de bundle ID**: la doc de `xtool` confirma que con cuentas gratuitas **prefija
  automáticamente el bundle ID** (p. ej. `XTL-1234.com.example.App`) porque dos cuentas no
  pueden compartir bundle ID; wildcard provisioning sólo con cuenta de pago. Impacto bajo
  para uso personal. [QF3]
- **Límites de cuenta gratuita** (conocidos de Apple, a confirmar en el spike): ~3 apps
  firmadas gratis simultáneas por dispositivo, hasta 10 App IDs por 7 días, y capabilities
  avanzadas (push remoto, App Groups, iCloud...) **no disponibles** sin cuenta de pago.
  [QF3] [assumption]
- **Comparativa con Apple Developer Program (~99 €/año)**: evita la caducidad de 7 días
  (certificados de 1 año), habilita todas las capabilities y permite distribución más
  amplia. Es la **excepción de coste acotada** ya contemplada en las reglas del proyecto.
  [memory:M1] El estudio recomienda **empezar por firma gratuita** (coherente con QF3=A y
  QF5=A) y reservar el pago como salida si la fricción resulta inasumible. [QF3] [QF5]

## 5. Impacto en autenticación (dependencia de backend a vigilar)

La PWA usa access token en memoria + refresh token en cookie `HttpOnly`. Un cliente nativo
Swift **no gestiona cookies de navegador**, por lo que: [QF4]

- El cliente Swift debe guardar el refresh token en el **iOS Keychain** (almacenamiento
  seguro nativo), **nunca en claro** — regla durable de seguridad del proyecto. [QF4]
  [memory:M2]
- Riesgo/dependencia: el endpoint `/auth/refresh` hoy lee el refresh token de la **cookie
  HttpOnly**. Si no acepta el token por header/body, el cliente nativo no podrá refrescar y
  haría falta un **ajuste mínimo del backend** (fuera del alcance de este intent, pero a
  registrar como dependencia). [QF4] → RAID (D-01). El frontend existente ya tiene un
  interceptor de auth con refresh que sirve de especificación del flujo. [QF4]

## 6. Alcance funcional de la primera versión (verificado contra el código)

Las 5 funciones núcleo elegidas [Q6] existen como features Angular reales (exploración
ligera del repo), lo que confirma su especificación de referencia:

| Función núcleo | Feature Angular de referencia | Servicio(s) core |
|----------------|-------------------------------|------------------|
| Login | `features/login` (+ `splash`) | `auth.service`, `auth.interceptor` |
| Mercado | `features/market` (bid dialog, sofascore) | vía `analytics`/mercado |
| Presupuesto | `features/budget` (overview, detail) | `budget.service` |
| Favoritos | `features/favorites` | `favorites.service` |
| Calculadora | `features/calculator` (feature propia) | — |

Corrección de un supuesto previo de intent-capture: **"Calculadora" es una feature propia
(`features/calculator`), no la de Finanzas**; "Favoritos" = `features/favorites`. [Q6] El
resto de pantallas (finances, stats, evolution, clausulable, classification, transactions,
my-roster, analytics) queda fuera de la primera versión. [Q6] [Q8]

## 7. Viabilidad por dimensiones

- **Técnica**: plausible; el principal desconocido es el spike de `xtool` (R-01) y el ajuste
  de auth (D-01). SwiftUI cubre de sobra las 5 pantallas. [QF1] [QF2] [QF4]
- **Económica**: 0 € recurrente con firma gratuita; el único coste potencial es el Apple
  Developer Program como salida opcional. [QF3] [memory:M1]
- **De esfuerzo**: alta (reescritura total del cliente), pero sin plazo y con el aprendizaje
  como valor explícito. [QF5] [Q1]
- **De entorno**: baja barrera (WSL ya operativo). [QF3b]

## Assumptions & Open Questions

- [assumption] Los límites exactos de cuenta gratuita de Apple (nº de apps, App IDs,
  capabilities) se confirmarán en el spike; aquí se citan de conocimiento general de la
  plataforma. [QF3]
- [assumption] Se asume que `/auth/refresh` depende de la cookie `HttpOnly` y podría requerir
  ajuste; debe verificarse leyendo el backend en un intent posterior. [QF4]
- [assumption] La caducidad de la firma gratuita (~7 días) y el flujo de reinstalación con
  `xtool dev` se validarán en el spike. [QF2] [QF3]
