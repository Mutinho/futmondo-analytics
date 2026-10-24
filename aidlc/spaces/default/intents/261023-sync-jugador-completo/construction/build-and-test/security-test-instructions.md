# Security Test Instructions

Estrategia **minimal**. Postura de seguridad del cambio:

- **SQL parametrizado**: el SELECT de `favorites_read` y el upsert usan
  `db.adapt_params`/placeholders; la migración usa DDL estática (nombres de
  columna fijos), sin interpolación de entrada de usuario.
- **Sin credenciales en logs**: la ruta de error del orquestador conserva el
  patrón actual (`str(e)`), sin token/password; congelado en
  `tests/test_sync_players_enrichment.py`.
- **Sin superficie nueva**: no hay endpoints ni dependencias nuevas; el contrato
  de `favorites/my` no cambia.

```bash
python -m pytest tests/test_sync_players_enrichment.py -q
```

`gitleaks` y `pip-audit` corren en el gate de CI del PR.
