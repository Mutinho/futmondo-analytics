# Requirements Analysis — Preguntas de clarificación (matchday-prizes-calc)

Intent: corregir el reparto del **premio de ranking por jornada** cuando hay
equipos **empatados a puntos**. Hoy `sync_prizes` asigna a cada equipo el premio
de su posición individual (según el orden que devuelve la API), sin detectar
empates. El comportamiento correcto de Futmondo (confirmado por el usuario con
el campeonato `592416daa3a2dd871a7a9956`, jornada 5): **sumar los premios de las
posiciones que ocupan los empatados y repartirlos a partes iguales entre ellos**.

Ejemplo: 2 equipos empatan ocupando 3ª (1.285.714) y 4ª (1.714.286) →
suma 3.000.000 → 1.500.000 a cada uno. Con 3 empatados se suman las 3 posiciones
y se divide entre 3.

---

## Q1. Alcance del arreglo: ¿solo el premio de ranking, o algún otro término?

El empate afecta al **premio por posición (ranking_prize)**. Los otros términos
—premio por puntos (`points_prize`), MVP, dream-team— no dependen de la posición
relativa. ¿Confirmas que el arreglo se limita al premio de ranking?

- A. Solo el premio de ranking (los empatados comparten la suma de sus posiciones); el resto de términos no cambia
- B. También revisar MVP/dream-team ante empates
- X. Other (please specify)

[Answer]: A

---

## Q2. Redondeo al repartir la suma entre los empatados

`suma_de_posiciones / N` puede no ser entero (p. ej. 3 empatados). Hoy los
importes se redondean con `round()` (redondeo a entero más cercano). ¿Cómo
repartimos?

- A. Redondear cada parte a entero con `round()` (mismo criterio que hoy); asumir posible descuadre de ±1 por redondeo
- B. Redondear pero **cuadrar la suma**: repartir el resto de la división para que la suma de las partes iguale exactamente la suma de los premios de las posiciones empatadas
- C. Mantener decimales (no redondear a entero)
- X. Other (please specify)

[Answer]: A (decisión del usuario: no se conoce con certeza cómo cuadra Futmondo el resto; se redondea cada parte con round() como hoy y se abordará el reparto exacto del resto si el caso llega a darse)

---

## Q3. Criterio de empate: ¿qué campo define "empatados"?

Los equipos se ordenan por sus puntos de la jornada. ¿El empate se determina por
el mismo número de **puntos de la jornada** (`points`)?

- A. Sí: empatan los equipos con el mismo valor de puntos de la jornada (`points`)
- B. Otro criterio (especifícalo)
- X. Other (please specify)

[Answer]: A

---

## Q4. Equipos con 0 puntos y miembros fuera de premio

Hoy solo entran al reparto de ranking los equipos "activos" (con puntos de
jornada > 0) y, si el campeonato limita `users_to_rank`, solo las primeras
posiciones premiadas. ¿Se mantiene ese comportamiento y la regla de empate se
aplica solo dentro del conjunto premiado?

- A. Sí: mantener exclusión de 0 puntos y el límite `users_to_rank`; los empates se agrupan solo entre posiciones premiadas
- B. Cambiar alguna de esas reglas (especifícalo)
- X. Other (please specify)

[Answer]: A

---

## Q5. Empate que cruza el borde de las posiciones premiadas

Si un grupo de empatados ocupa posiciones donde algunas premian y otras no
(p. ej. `users_to_rank` corta a mitad del grupo empatado), ¿qué se reparte?

- A. Sumar solo los premios de las posiciones premiadas dentro del grupo y repartir esa suma entre TODOS los empatados del grupo
- B. Sumar solo posiciones premiadas y repartir solo entre los empatados que caen en posición premiada
- C. No aplica / este caso no ocurre en la práctica; resolver de la forma más simple (A)
- X. Other (please specify)

[Answer]: A (aclaración del usuario: en este campeonato TODAS las posiciones premian — no hay corte por `users_to_rank` que parta un grupo de empatados —, por lo que el caso del borde no se da; la regla de empate se aplica sobre el conjunto completo de equipos con puntos de jornada > 0)

---

## Q6. Recálculo de datos históricos ya guardados

Al desplegar el arreglo, el próximo sync recalculará los premios (el código ya
recalcula todas las rondas, no solo las nuevas). ¿Quieres que la corrección se
aplique retroactivamente a jornadas pasadas ya premiadas (como la jornada 5 del
ejemplo)?

- A. Sí: al recalcular, corregir también las jornadas pasadas afectadas por empates (comportamiento retroactivo, coherente con el recálculo total actual)
- B. No: aplicar solo a jornadas nuevas; congelar lo ya repartido
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de lo acordado para la mejora del cálculo de premios de jornada:

- El arreglo se limita al **premio de ranking**; premio por puntos, MVP y dream-team no cambian (Q1).
- Regla de empate: cuando N equipos empatan a puntos de jornada, se **suman los premios de las N posiciones que ocupan** y se reparte a partes iguales entre ellos; cada parte se **redondea con `round()`** como hoy, y el reparto exacto del resto (cuando la división no es entera) se abordará solo si el caso llega a darse (Q2).
- Empate = mismo valor de **puntos de la jornada** (`points`) (Q3).
- Se mantiene la exclusión de equipos con 0 puntos y el límite `users_to_rank`; los empates se agrupan dentro del conjunto premiado (Q4).
- En este campeonato **todas las posiciones premian**, así que el caso de empate que cruza el borde de posiciones premiadas no se da (Q5).
- La corrección se aplica **retroactivamente** al recalcular (el sync ya recalcula todas las rondas), por lo que la jornada 5 del ejemplo se corregirá en el próximo sync (Q6).

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
