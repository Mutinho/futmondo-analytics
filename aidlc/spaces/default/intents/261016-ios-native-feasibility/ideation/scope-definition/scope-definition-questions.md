# Scope Definition — Preguntas de clarificación

> Ya decidido (no se re-pregunta): ruta Swift/SwiftUI nativo + `xtool` (WSL); coste 0 € con
> firma gratuita (~7 días); iOS-only, uso personal; backend intacto; sin App Store pública;
> 5 funciones núcleo = Login, Mercado, Presupuesto, Favoritos, Calculadora; sin plazo.
> Esta etapa fija la FRONTERA in/out y la SECUENCIACIÓN por fases.

## QS1. Secuenciación de las fases: ¿en qué orden prefieres construir?

El feasibility recomienda un spike temprano de la cadena `xtool`. Dentro de eso, ¿qué criterio ordena las fases?

- A. Risk-first: primero el **spike de `xtool`** (app Swift mínima instalada en el iPhone) + **Login** (valida auth + Keychain + la cadena de build end-to-end), antes de cualquier pantalla de datos. Reduce el riesgo R-01 cuanto antes.
- B. Value-first: primero las pantallas que más usas (p. ej. Mercado), aunque el riesgo técnico se valide más tarde.
- C. Dependency-first: seguir el orden natural de dependencias (Login → datos → cálculos).
- D. Not yet defined — recomiéndame tú el orden.
- X. Other (please specify)

[Answer]: A. Risk-first: primero el spike de `xtool` (app Swift mínima instalada en el iPhone) + Login (valida auth + Keychain + la cadena de build/firma/deploy end-to-end), antes de cualquier pantalla de datos. Ataca R-01 cuanto antes.

## QS2. ¿Cuál es el MVP mínimo que ya aporta valor, dentro de las 5 funciones núcleo?

Para marcar el "primer hito usable" aunque falten pantallas.

- A. Walking skeleton: spike `xtool` + Login funcionando en el iPhone (sin pantallas de datos aún). Es el MVP técnico que demuestra viabilidad.
- B. Login + Mercado: lo mínimo que ya sirve para algo útil a diario.
- C. Login + Presupuesto + Calculadora: el núcleo "financiero".
- D. Las 5 funciones completas; no considero MVP parcial.
- E. Not yet defined.
- X. Other (please specify)

[Answer]: X. MVP mínimo = Login + Presupuesto + Mercado. Login valida la cadena técnica; Presupuesto + Mercado dan el primer valor de uso real. Favoritos y Calculadora quedan para una fase posterior dentro de las 5 núcleo.

## QS3. Prioridad relativa de las 5 funciones (must-have vs. nice-to-have en la v1 nativa):

Marca cuáles son imprescindibles en la primera versión nativa y cuáles podrían esperar.

- A. Todas must-have (las 5 van sí o sí en la v1).
- B. Must: Login + Mercado + Presupuesto. Nice-to-have (pueden ir después): Favoritos, Calculadora.
- C. Must: Login + Presupuesto + Calculadora. Nice-to-have: Mercado, Favoritos.
- D. Recomiéndame tú el reparto must/nice.
- X. Other (please specify)

[Answer]: B. Must-have v1: Login + Mercado + Presupuesto. Nice-to-have (fase posterior): Favoritos, Calculadora.

## QS4. ¿Hay algo que quieras mover explícitamente FUERA del alcance de este estudio/plan que no se haya dicho ya?

El in/out ya recoge: fuera App Store pública, Android, cambios de backend (salvo D-01 como dependencia a vigilar). ¿Algo más?

- A. Nada más; la frontera actual es correcta.
- B. Fuera también: notificaciones push (requieren cuenta de pago; coherente con R-03).
- C. Fuera también: widgets de pantalla de inicio en la v1 (aunque `xtool` los soporte), dejarlos para una fase posterior.
- D. Not applicable.
- X. Other (please specify)

[Answer]: B + variante de C. Fuera de v1 (implementación): notificaciones push (DEFINITIVO: requieren cuenta de pago/APNs, inviable a coste 0 €, coherente con R-03) y widgets de pantalla de inicio. MATIZ sobre widgets: NO quedan "fuera del todo" — el estudio DOCUMENTA su viabilidad con `xtool` + firma gratuita (App Extensions soportadas: producto extra en `Package.swift` + `extensions` en `xtool.yml` + `Info.plist`) y esboza qué widget tendría sentido (p. ej. resumen de presupuesto/mercado), marcándolos como **fase futura / fast-follow**, no en el MVP ni en la v1 de las 5 funciones.

<!-- Nota: puedes responder en modo Guía (una a una), Edición, o Chat. -->
