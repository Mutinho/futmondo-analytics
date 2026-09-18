# Interview — practices-discovery (260918-matchday-prizes-calc)

Re-run brownfield. Las 5 secciones estándar (Way of Working, Walking Skeleton,
Testing Posture, Deployment, Code Style) ya están afirmadas en la línea base y
el draft del lead solo las matiza para el área de premios. Estas preguntas
resuelven las incertidumbres que el draft y las revisiones ciegas no pudieron
establecer por sí solas. Son la fuente de verdad.

---

## Q1. Alcance del cambio en la fórmula de premios

La fórmula de premios vive entera dentro de una función grande (`sync_prizes`,
~300 líneas dentro de un fichero de ~84 KB). ¿Cómo de lejos llega este intent?

- A. Extraer la fórmula a una función/módulo estrecho y testeable (lo recomendado por el análisis), corrigiendo el cálculo ahí, sin engordar el fichero grande
- B. Corregir el cálculo *in situ* dentro de la función actual, apoyándonos solo en la red de tests de caracterización, sin extraer nada
- C. Mixto: extraer solo las partes que haya que tocar para el arreglo; el resto se queda donde está
- X. Other (please specify)

[Answer]: A

---

## Q2. Qué ramas de la fórmula hay que congelar con tests ANTES de tocar

Antes de cambiar nada, hay que "fotografiar" con tests el comportamiento actual.
¿Qué partes son de captura obligatoria?

- A. Todas las ramas: premio por puntos, condición de ronda completa, ranking (mejores/peores), MVP, dream-team, jornada adelantada/negativa y el borrado defensivo de filas
- B. Solo el subconjunto crítico que el arreglo va a tocar (a decidir en diseño)
- X. Other (please specify)

[Answer]: A

---

## Q3. ¿Hay comportamientos actuales que consideres un bug a corregir?

Esto define si algún test de la "foto inicial" describe algo que vamos a cambiar
a propósito (y por tanto se retirará de forma trazable), o si solo buscamos
fiabilidad sin alterar los importes que ya salen hoy.

- A. Sí, hay bugs concretos en el cálculo que este intent debe corregir (los importes actuales pueden cambiar a propósito) — los detallaré en requisitos
- B. No: el objetivo es fiabilidad/robustez sin cambiar los importes que se calculan hoy
- C. No lo sé todavía; que emerja durante el análisis de requisitos y la caracterización
- X. Other (please specify)

[Answer]: C

---

## Q4. Cobertura de tests

Hoy no hay un umbral de cobertura que bloquee. ¿Lo mantenemos así?

- A. Mantener el 80% como referencia global no-bloqueante, exigiendo solo que existan tests para los caminos nuevos y de error de los premios (línea base actual)
- B. Activar un piso/ratchet de cobertura bloqueante para las piezas de premios en este intent
- X. Other (please specify)

[Answer]: A

---

## Q5. Paridad del chequeo de despliegue con el gate de PR

El chequeo que corre al desplegar (`verify`) ya incluye escaneo de secretos,
pero NO calcula cobertura (`--cov`), a diferencia del gate de Pull Request.

- A. Diferir: dejarlo como está; se aborda en un futuro diseño de pipeline, no en este intent
- B. Abordarlo en este intent: que `verify` también corra con `--cov` para no perder señal de cobertura al desplegar
- X. Other (please specify)

[Answer]: A

---

## Q6. Deuda técnica adyacente (doble sentido de "puntos" e identidad por nombre)

En la zona de premios hay dos deudas conocidas: la palabra "puntos" significa
dos cosas distintas (métrica vs dinero), y jugadores/equipos se casan por nombre
(frágil). ¿Entran en el alcance de este intent?

- A. Fuera de alcance: documentarlas como deuda conocida y no tocarlas ahora
- B. Dentro de alcance: abordarlas como parte de esta mejora
- C. Solo la desambiguación de "puntos" (naming) dentro de alcance; la identidad por nombre queda como deuda
- X. Other (please specify)

[Answer]: A
