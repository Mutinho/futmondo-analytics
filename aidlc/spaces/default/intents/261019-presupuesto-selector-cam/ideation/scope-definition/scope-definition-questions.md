# Scope Definition — Questions (F2)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.
> Modo "Guíame": recomendación en cada pregunta; decides tú.

## Q1 — Mínimo de navegación (recoge el finding advisory R-04)

Para blindar el límite y evitar scope creep, ¿cuál es el mínimo de navegación que entra en F2?

- A. **Solo navigation bar arriba** (`NavigationStack` + `.toolbar`) con Presupuesto + el menú del selector; sin tab bar de abajo. La tab bar llega en un intent posterior cuando haya ≥2 secciones.
- A′. **Navigation bar arriba + `TabView` de abajo con UNA sola pestaña "Presupuesto"** como andamiaje de navegación. El `TabView` nativo adopta automáticamente el material **Liquid Glass de iOS 26** (translúcido, redondeado, transición fluida) compilando con el SDK reciente — coste 0 €, sin librerías. El selector de campeonato va en la navigation bar de arriba (no en la tab bar). Las futuras secciones (F3/F4) sólo añaden pestañas, sin re-estructurar la raíz. **(elegida)**
- B. Shell de tab bar completo preparado para varias secciones (más alcance).
- X. Other (please specify)

[Answer]: A′

## Consolidated Summary Confirmation

Resumen de Scope Definition:

- **In scope**: pantalla de Presupuesto (lista nativa solo-lectura con métricas de `TeamBudget`, tokens de dinero, ordenación, estados carga/error); selector de campeonato en la navigation bar de arriba (recarga + `UserDefaults`); capa de datos nativa reutilizando `NetworkClient`/auth de F1; **andamiaje de navegación `TabView` con UNA sola pestaña "Presupuesto"** (Liquid Glass iOS 26, coste 0 €) + `NavigationStack`/`.toolbar` (finding R-04 resuelto, opción A′).
- **Out of scope / follow-up**: detalle de equipo, diálogo de premios, **pestañas/secciones adicionales del `TabView`**, otras pantallas, toggle tabla/cards. **Cero cambios de backend/infra/CI.**
- **MoSCoW**: Must M1–M6 (M6 = andamiaje `TabView`), Should S1 (ordenación), Could C1 (afinados de fidelidad), Won't W1–W4.
- **Restricciones**: coste 0 €, sin cambios de backend, tema Angular como verdad, sesión F1 intacta, verificación `swift test`+dispositivo.

¿Does this all look correct?

[Answer]: Looks correct
