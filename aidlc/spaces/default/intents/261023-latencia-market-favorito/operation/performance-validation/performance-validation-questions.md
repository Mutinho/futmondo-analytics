# Performance Validation — Preguntas

Intent `261023-latencia-market-favorito`. El objetivo y método ya están fijados
en `nfr-requirements/performance-requirements.md` (NFR1.1 p95 < 0,5 s
`favorites/my`; NFR1.2 p95 < 0,8 s `market/today`; ≥ 30 peticiones secuenciales
autenticadas, `time_total`, p50/p95/p99, warm-up descartado). Las preguntas
abajo resuelven **cómo y dónde** medimos ahora. Cada ⭐ es la recomendación.

---

## Q1. Entorno de medición (realidad importante)

El código optimizado está en la rama `feat/ios-native-app` y **no está
desplegado** en Fly.io: la producción actual ejecuta todavía el código con la
llamada viva. Además no hay un backend local corriendo con Neon sembrado. ¿Cómo
validamos el objetivo?

- A. ⭐ **Validación en dos partes:** (1) **ahora**, validación *analítica* +
  *micro-benchmark de la capa nueva* con el fake/datos sembrados (demuestra que
  `read_favorites`/`read_market_catalog` son lecturas O(favoritos) sin I/O de red
  — la causa raíz de la latencia eliminada), y se documenta el presupuesto de
  latencia esperado; (2) la **medición p95 real contra el endpoint** queda
  **registrada como pendiente de ejecutar tras el deploy** (owning step: primer
  despliegue de esta rama), con el comando exacto listo para correr. Es honesto:
  no fabricamos un número de producción que hoy no podemos medir.
- B. Desplegar la rama a Fly.io ahora para medir en caliente. (Implica merge/push
  + deploy, que es una acción de alto impacto fuera del alcance de este intent y
  requiere tu decisión explícita de desplegar.)
- C. Montar un backend local con Neon sembrado y medir localmente. (Añade setup
  de entorno no trivial; la latencia local no es comparable a producción.)
- X. Other (please specify)

[Answer]: A

---

## Q2. Criterio de aceptación del objetivo (dado Q1-A)

- A. ⭐ Se da por **validada la causa raíz** (eliminación de las llamadas vivas
  en la ruta normal de `favorites/my`, medible en la capa) y el **presupuesto de
  latencia** (<0,5 s / <0,8 s) como objetivo; la **confirmación empírica p95** se
  marca `Pending-deploy` en la matriz NFR con el comando y el umbral listos. El
  intent se cierra con esa condición explícita documentada.
- X. Other (please specify)

[Answer]: A
