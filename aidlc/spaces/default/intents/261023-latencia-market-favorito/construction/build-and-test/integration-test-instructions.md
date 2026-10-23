# Integration Test Instructions

Estrategia **minimal**: la frontera clave (router → capa `sync_read` → fake DB,
y la ruta de fallback vivo) está cubierta a nivel de endpoint por
`tests/test_sync_read_endpoints.py`, que ejercita:

- `favorites/my` servido desde sync **sin** llamada viva.
- `favorites/my` cae a la ruta viva en sync-miss + log.
- `market/today` catálogo desde caché + pujas vivas.
- Degradación de pujas a cero + warning cuando la llamada de pujas falla.
- Ausencia de credenciales en los logs.

Comando:

```bash
python -m pytest tests/test_sync_read_endpoints.py -q
```

No se requieren tests de integración adicionales (no hay nuevas fronteras
externas; la única llamada viva es la de pujas, ya doblada en los tests).
