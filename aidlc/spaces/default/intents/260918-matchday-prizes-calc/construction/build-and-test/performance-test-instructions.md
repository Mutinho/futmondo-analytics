# Performance Test Instructions — matchday-prizes-calc

**NO APLICA / fuera de alcance.** El intent no introduce requisitos de
rendimiento nuevos: el cálculo es una transformación pura sobre unas pocas
decenas de equipos por ronda, en un camino batch (cron de sync), no en la ruta
de lectura del usuario. El coste de la extracción es despreciable y no cambia el
perfil de rendimiento del sync.

- No se definen SLOs ni pruebas de carga (coste 0 €; sin servicios de pago).
- La ruta de lectura de finanzas (que sí ve el usuario) no se modifica.
