# Security Test Instructions — NO APLICA generación nueva (estrategia Minimal)

> Perspectiva del ingeniero de seguridad (devsecops), integrada por la QA lead.

## Decisión

Estrategia **Minimal**, refactor de estructura sin nueva superficie de ataque. No
se generan tests de seguridad nuevos. Las garantías de seguridad relevantes ya
están cubiertas por controles existentes que este intent **preserva**.

## Controles de seguridad verificados (existentes, preservados)

- **Sin credenciales en excepciones/logs** (BR4.2): el orquestador extraído
  preserva el manejo de errores sin incluir password/token en mensaje/`repr`/
  `exc_info`. El test de caracterización aserta el modo de fallo sin fuga.
- **gitleaks** (gate de CI bloqueante) escanea el código y los tests nuevos; los
  tests usan fakes en memoria, **sin credenciales/tokens reales**.
- **Sin nueva superficie**: no hay endpoints, autenticación ni entradas de usuario
  nuevas; el contrato REST público no cambia. `data_manager_v2.py` intacto (sin
  nuevo SQL ni inyección).
- `JWT_SECRET` no-default en arranque (NFR1.1) sin cambios.

## Ejecución

Ninguna acción de test de seguridad nueva en este intent. El escaneo de secretos
y el lint corren en el gate de CI bloqueante como de costumbre.
