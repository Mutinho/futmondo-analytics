# Security Test Instructions

Estrategia **minimal**: la postura de seguridad (NFR5) se verifica con los tests
de la capa nueva, ya ejecutados en la suite:

- **SQL parametrizado** (NFR5.3): toda consulta de `sync_read` usa `db.adapt_params`
  / placeholders `?`; la IN-clause construye solo `?` (sin interpolación de
  valores). Verificado por lectura + los tests que ejercitan el SQL real.
- **Sin credenciales en logs/errores** (NFR5.4): aserción explícita en
  `tests/test_sync_read_endpoints.py` de que ningún log contiene el token.
- **Auth/scoping** (NFR5.1/5.2): sin cambios; `player_favorites` filtra por
  `user_id`; las pujas son del usuario autenticado.

Comando (ya cubierto por la suite):

```bash
python -m pytest tests/test_sync_read_endpoints.py -q
```

El escaneo de secretos (`gitleaks`) y `pip-audit` corren en el gate de CI del PR.
