# NFR Validation Matrix — Optimización de latencia

Target vs. actual. Decisión del propietario (Q1-A/Q2-A): causa raíz validada
ahora; medición empírica p95 `Pending-deploy`.

| NFR | Target (pass/fail) | Método | Actual | Veredicto |
|---|---|---|---|---|
| NFR1.1 | `favorites/my` p95 < 0,5 s | ≥30 req secuenciales, p95 interpol. lineal, post-deploy | Causa raíz eliminada (0 llamadas vivas en ruta normal); presupuesto <0,5 s; medición empírica pendiente | **Validado (causa raíz) / Pending-deploy (p95 empírico)** |
| NFR1.2 | `market/today` p95 < 0,8 s | igual | Catálogo desde caché; 1 llamada viva (pujas) irreducible; medición empírica pendiente | **Validado (causa raíz) / Pending-deploy (p95 empírico)** |
| NFR1.3 | ≤ patrón `balances` (~0,4 s) | comparación en la misma corrida | `favorites/my` sin llamadas vivas ≈ lecturas Neon ≤ `balances`; a confirmar post-deploy | **Pending-deploy** |
| NFR1.4 | reportar p50/p95/p99 | del script | comando listo reporta los tres | **Listo (post-deploy)** |
| NFR2 | frescura: valores/stats última sync; pujas coherentes tras operar | diseño + código | pujas leídas en vivo (coherencia por construcción); valores desde sync | **Met** |
| NFR3 | coste 0 | revisión | sin dependencias nuevas; solo Neon/Fly.io free | **Met** |
| NFR5 | errores tipados / SQL param / sin credenciales | tests | aserciones verdes en la suite | **Met** |
| NFR6 | sin cambio de esquema/contrato | caracterización | solo lectura; contrato byte-identical congelado | **Met** |

## Condición de cierre explícita

El intent se cierra con la **causa raíz de la latencia validada** (eliminación
de las llamadas vivas en la ruta normal de `favorites/my`, medible en la capa) y
el **objetivo p95 fijado con comando y umbral listos**. La **confirmación
empírica p95** (NFR1.1/NFR1.2/NFR1.3) queda **`Pending-deploy`**: debe ejecutarse
el comando de `load-test-plan.md` tras el primer despliegue de la rama
`feat/ios-native-app` a Fly.io, verificando p95 < 0,5 s (favorites) y < 0,8 s
(market). Este pendiente está documentado y con dueño (el despliegue), no es un
hueco silencioso.
