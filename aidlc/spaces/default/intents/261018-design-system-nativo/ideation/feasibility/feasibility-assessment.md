# Feasibility Assessment — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, xtool, WSL, Apple HIG, Google Stitch) verbatim en inglés.
> Entregable de análisis (prosa); estimaciones conservadoras y supuestos marcados conforme a la disciplina de ideación. Consume: `intent-statement.md`.

## 1. Veredicto de viabilidad

**GO**. Entregar una capa de diseño reutilizable en SwiftUI (tokens de color claro/oscuro, tipografía con Dynamic Type, espaciado y componentes base) es **técnicamente plausible con holgura** usando únicamente el SDK de Apple, sin dependencias de pago ni infraestructura nueva. [Q1] [Q4] El riesgo no está en "si se puede", sino en la **fidelidad** de reproducir un diseño externo y en la **transversalidad** del soporte claro/oscuro + Dynamic Type; ambos son gestionables. [Q7]

## 2. Viabilidad por dimensiones

- **Técnica**: SwiftUI cubre de sobra tokens, tipografía con Dynamic Type, color sets claro/oscuro y componentes base (botones, campos, tarjetas, estados de carga/error) con SDK de Apple. La capa es **autocontenida** y se apoya en la estructura SwiftPM/`xtool.yml` y convenciones del código iOS de F1. [Q1] [Q3]
- **Económica**: coste 0 € recurrente — sólo SDK de Apple, ninguna dependencia de pago ni servicio. La excepción acotada de publicación nativa (Apple Developer Program) **no se activa** en este intent. [Q4]
- **De esfuerzo**: moderado; sin plazo (proyecto personal). Existe una **curva de aprendizaje en SwiftUI** (experiencia aún limitada) que se registra como riesgo, no como bloqueo. [Q3] [Q4]
- **De entorno**: baja barrera — cadena `xtool` desde WSL ya validada en F1 con firma gratuita; no se usa AWS ni infraestructura de pago. [Q3] [Q6]
- **Regulatoria**: sin requisitos (PCI/HIPAA/SOC2/residencia). Una capa de diseño no maneja datos personales ni de pago; la regla durable de no almacenar credenciales en claro se preserva y no la toca este intent. [Q2]

## 3. Incertidumbre técnica principal

El riesgo dominante es la **fidelidad de reproducción** en SwiftUI del tema del frontend Angular existente (Material 3 con paleta primaria verde y terciaria violeta, Roboto, modo claro/oscuro y tokens semánticos propios definidos en `angular-app/src/styles.scss`). Material 3 y SwiftUI no son 1:1, así que hay que mapear los roles de color y la escala tipográfica a equivalentes nativos; donde no haya equivalente directo se usan las guías de Apple (HIG) a coste 0 €. Le siguen la **transversalidad de claro/oscuro + Dynamic Type** (que todos los componentes respondan sin reglas ad-hoc por pantalla) y **revestir F1 sin regresión** (aplicar la capa al login ya construido sin cambiar su comportamiento). Los tres se detallan en el RAID. [Q7] [Q8]

## 4. NO-APLICA (adaptación al stack real)

| Aspecto estándar de la etapa | Estado |
|------------------------------|--------|
| Servicios/cuentas AWS | NO-APLICA; stack Fly.io + Neon (backend) y app nativa iOS con `xtool`. La capa de diseño es puramente cliente iOS. [Q6] |
| Compliance regulatorio (PCI/HIPAA/SOC2/residencia) | NO-APLICA; capa de diseño sin datos sensibles. [Q2] |
| Dimensionamiento de mercado / competencia | NO-APLICA; Market Research saltada (intent interno, un único usuario). |

## Assumptions & Open Questions

- [assumption] La referencia de diseño es el tema del frontend Angular existente (`angular-app/src/styles.scss`): Material 3 paleta verde/violeta, Roboto, claro/oscuro y tokens semánticos propios. Google Stitch queda **descartado** (decisión del propietario, 2026-10-18). El mapeo exacto de roles de color Material 3 → SwiftUI y de la escala tipográfica se concretará en las etapas de mockups. [Q8] [Q7]
