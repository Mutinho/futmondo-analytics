# Performance Test Instructions

Estrategia **minimal**: no se generan tests de carga nuevos aquí. El objetivo de
rendimiento (NFR1.1 p95 < 0,5 s `favorites/my`; NFR1.2 p95 < 0,8 s
`market/today`) se verifica en la stage dedicada **Performance Validation**
(owning stage), con el método fijado en `nfr-requirements/performance-requirements.md`:

```bash
# ≥ 30 peticiones secuenciales autenticadas, time_total, percentil por
# interpolación lineal, p50/p95/p99; primera petición (warm-up) descartada.
# Contra producción Fly.io o entorno equivalente.
```

Este target queda **diferido** a Performance Validation; en Build and Test se
marca `Unverified` con su owning stage registrado (no contribuye al resultado de
esta stage, pero tiene dueño explícito programado a continuación).
