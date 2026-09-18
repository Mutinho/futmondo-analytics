# Delivery Planning — Mapa de dependencias externas (matchday-prizes-calc)

Trabajo autocontenido en la IA + el equipo; no hay hand-offs de otros equipos ni
aprobaciones externas que bloqueen el Bolt.

| Ítem | Tipo | Dueño | Bloquea | Plan si se retrasa |
|---|---|---|---|---|
| API Futmondo (datos de ronda) | Dependencia de datos externa (ya integrada) | Futmondo | Ninguno en desarrollo: los tests usan fakes; en producción el sync ya la consume | N/A (fakes en test; sin cambio de integración) |

No hay ventanas de disponibilidad de datos, tiempos de aprobación externos ni
entregas de otros equipos pendientes.
