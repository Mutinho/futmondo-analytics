# Delivery Planning — Riesgo y racional de secuenciación (matchday-prizes-calc)

## Secuenciación

Con una sola unidad de trabajo, hay **un único Bolt** y no hay decisión de orden
económico entre Bolts (no aplican modelos tipo WSJF ni walking-skeleton-first).
La secuencia respeta trivialmente el DAG de Units Generation (sin aristas).

## Orden interno del Bolt (dentro de U1)

El único orden relevante es intra-unidad y viene impuesto por la postura de
testing afirmada (characterization-first, test-after):

1. Caracterizar todas las ramas de `sync_prizes` (red de seguridad, NFR1).
2. Extraer el cálculo puro (`PrizeCalculator`) y reducir `sync_prizes` a
   orquestador.
3. Implementar la regla de empate (FR1) y escribir los tests del nuevo contrato.

## Riesgos principales y mitigación

| Riesgo | Mitigación |
|---|---|
| Romper el comportamiento actual de `sync_prizes` (cobertura directa cero hoy) | Caracterización previa obligatoria de TODAS las ramas antes de tocar (NFR1); suite en verde. |
| Coste/lentitud de tests por dependencia de la API Futmondo con `time.sleep` | Fakes de la API y de la persistencia (patrón `conftest.py`), coste 0 € (NFR3). |
| División no entera al repartir entre N empatados (OQ1) | Redondeo `round()` por parte (decidido); registrado como cuestión abierta a revisar si se materializa. |
| Engordar los god-files al tocar el cálculo | Extracción a `services/prizes/` puro; SQL/I·O fuera del cálculo (NFR4). |

## Heurística usada

No aplica un modelo de scoring (un solo Bolt). Racional: riesgo-primero dentro
de la unidad vía characterization-first.
