# Initiative Brief — App nativa iOS (Swift) de Futmondo, build con xtool

> One-pager que compila la fase de ideación para la decisión go/no-go. Fuentes: todos los
> artefactos de ideación de este intent.

## Intent y problema

Convertir Futmondo Analytics (hoy PWA Angular) en una **app iOS nativa (Swift/SwiftUI)**,
por el valor de una experiencia nativa real y como ejercicio técnico. El reto: hacerlo
**sin Mac** (sólo Windows + WSL) con la herramienta `xtool`, y a **coste recurrente 0 €**
usando firma gratuita de Apple (que caduca ~7 días). [Q1] [desc] [QF1]

## Validación de la ruta técnica

- `xtool` (doc oficial verificada) construye paquetes SwiftPM en apps iOS, firma e instala
  desde Linux/WSL; en Windows funciona vía WSL (Swift 6.4 + usbmuxd + USB passthrough). Encaja
  de forma natural con Swift nativo puro. [QF2]
- Entorno favorable: WSL ya operativo. [QF3b]
- El código Angular existente se usa como **especificación funcional de referencia** (no se
  porta); se reutiliza el **backend FastAPI intacto** (HTTP) y el conocimiento de dominio.
  [QF1] [QF4]

## Viabilidad y riesgos

- **GO condicionado** al spike F0 que valide la cadena `xtool` end-to-end (R-01, riesgo
  principal). [QF2]
- Firma gratuita: caducidad ~7 días (R-02) y bundle ID prefijado (confirmado por doc);
  capabilities de pago (push) fuera (R-03). [QF3]
- Dependencia a vigilar: `/auth/refresh` basado en cookie `HttpOnly` podría requerir un
  ajuste mínimo del backend para clientes nativos (D-01); refresh token en **Keychain**.
  [QF4] [memory:M2]

## Frontera de alcance

- **Dentro (v1)**: Login, Mercado, Presupuesto (MVP) → luego Favoritos, Calculadora.
  Exploración documentada de widgets. [QS2] [QS3] [QS4]
- **Fuera**: App Store pública, Android, cambios de backend (salvo D-01), push, widgets en
  v1, pantallas no núcleo. [Q8] [QS4]

## Secuenciación (risk-first)

F0 spike `xtool` → F1 Login (red + auth + Keychain) → F2 MVP (Presupuesto + Mercado) → F3
núcleo (Favoritos + Calculadora) → fast-follow opcional (widget). [QS1] [QS2]

## Coste

0 € recurrente con firma gratuita. Apple Developer Program (~99 €/año) sólo como salida
opcional si la fricción del refirmado resulta inasumible — excepción de coste de distribución
ya contemplada en las reglas del proyecto. [memory:M1] [QF3]

## Equipo

Decisor y ejecutor único (propietario); sin coordinación multi-equipo. [Q7]

## Recomendación go/no-go

**GO condicionado** [QA3]: estudio y ruta aprobados; el primer paso de una futura
construcción sería el spike F0. Si el spike falla, se reconsidera ruta/coste. Decisión
reversible y de bajo coste (sin plazo). [QA3] [QF5]

## Assumptions & Open Questions

- [assumption] La viabilidad definitiva de la ruta depende del spike F0 (no validado en
  vivo). [QF2]
- [assumption] D-01 (ajuste de `/auth/refresh`) se confirmará leyendo el backend en un intent
  posterior. [QF4]
