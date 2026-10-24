# Performance Test Instructions

No aplica un test de carga nuevo en este intent. Es un cambio de completitud de
datos, no de latencia: `favorites_read` sigue siendo una lectura desde `players`
(añade columnas al mismo SELECT; no añade llamadas vivas). El objetivo de
latencia (<0,5 s) ya se validó en el intent de latencia anterior y no se degrada
aquí (mismo patrón de lectura). No hay target de rendimiento nuevo que medir.
