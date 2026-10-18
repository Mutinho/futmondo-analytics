# Intent Statement — Spike de la cadena `xtool` (B-01)

## Problem Statement

El estudio de viabilidad de app nativa iOS (intent `261016-ios-native-feasibility`) concluyó
**GO condicionado** a validar en vivo, antes de reescribir nada, que la cadena `xtool`
funciona end-to-end desde Windows/WSL. [desc] Este spike resuelve ese riesgo (R-01): comprobar
que una app Swift/SwiftUI mínima se puede **construir, firmar (con Apple ID gratuito) e
instalar** en un iPhone 13 Pro físico usando `xtool` desde WSL, y que **arranca** en el
dispositivo. [desc] [Q1] El spike atraviesa de principio a fin las tres dimensiones del riesgo
—toolchain WSL, firma gratuita e instalación en dispositivo— sin acotarse a una sola. [Q2]

## Target Customer

El beneficiario es **el único mantenedor del proyecto**. El resultado habilita la decisión
go/no-go de reescribir el cliente nativo (los proto-Units B-02…B-08) sobre la base `xtool` +
firma gratuita, y además deja una **guía reproducible (runbook)** para montar el entorno en el
futuro. [Q4]

## Success Metrics

- **DONE binario**: una app Swift/SwiftUI mínima **arranca en el iPhone 13 Pro físico**,
  construida+firmada+instalada íntegramente con `xtool` desde WSL, con firma de Apple ID
  gratuita. [Q1]
- **Cobertura del riesgo**: la validación ejercita la cadena completa (build Swift 6.4 → firma
  gratuita → instalación en dispositivo → arranque), no un solo eslabón. [Q2]
- **Entregables conservados**: la app mínima desechable (código Swift/SwiftUI +
  `xtool.yml`/`Package.swift`), una nota de hallazgos (qué funcionó, pasos, bloqueos, límites
  observados de la cuenta gratuita) y un runbook paso a paso del entorno WSL+`xtool`. [Q5]

## Initiative Trigger

Es el **camino crítico risk-first** del backlog de viabilidad: la reescritura del cliente
nativo no debe empezar hasta confirmar que la cadena de build/firma/instalación es viable en
el entorno real (WSL + iPhone 13 Pro). [desc] El montaje del toolchain (Swift 6.4, usbmuxd,
USB passthrough) **no está validado en vivo** hoy, por lo que la validación temprana evita
invertir esfuerzo de reescritura sobre una base no probada. [Q3]

## Initial Scope Signal

- **Workflow-selected scope**: `bugfix` (plan custom `ios-xtool-spike`, aplicado solo a este
  trabajo). [scope] (workflow-selected)
- **Límite de producto confirmado**: el spike es **solo la cadena de toolchain con una app de
  prueba trivial**. Quedan **fuera** cualquier pantalla real (login, mercado, presupuesto…), la
  capa de red hacia `/api/v1/*`, el auth con Keychain, el ajuste de `/auth/refresh` (D-01) y
  CI/distribución. [Q6]
- **Postura de coste**: estrictamente **firma gratuita** (Apple ID sin pago), coherente con el
  mandato de coste 0 €; si la firma gratuita no bastara, el spike lo documenta como hallazgo y
  **no se compra** el Apple Developer Program. [Q7] [memory:M1]

## Assumptions & Open Questions

- [assumption] Se dispone de un **Apple ID gratuito** y de **WSL operativo**; el resto del
  toolchain (Swift 6.4, usbmuxd/libimobiledevice, USB passthrough) se instala y documenta
  dentro del spike. [Q3]
- [assumption] La **caducidad ~7 días** de la firma gratuita y el flujo de refirmado quedan
  **fuera del foco** de este spike (materia del proto-Unit B-09); aquí solo se observa y anota
  si aflora. [Q2]
