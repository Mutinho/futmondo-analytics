# Security Test Instructions — Durabilidad del estado

> Etapa Build and Test (Construction). Estrategia **Standard**. Este intent toca directamente
> seguridad de credenciales (FR5/NFR1), así que —aunque Standard no exige un set separado de
> seguridad— se documentan aquí los tests de seguridad relevantes, que ya viven en los archivos de
> test de u1 y se ejecutan en la suite. Coste 0 €.

## Alcance de seguridad de este intent

El objetivo de seguridad es **no reintroducir la contraseña Futmondo en claro** al hacer durable el
estado (FR5.1/FR5.2, NFR1), y mantener el guard de arranque `JWT_SECRET` no-default (NFR1.1).

## Tests de seguridad (ya implementados en u1)

Archivo `backend/tests/test_durable_session_service.py` y
`test_durable_session_repository.py`:

- **`test_protect_stores_ciphertext_not_plaintext`**: escanea los bytes persistidos y verifica que la
  contraseña en claro NO aparece; solo `protected_material` (ciphertext Fernet) + `scheme`.
- **`test_reauth_material_repr_is_redacted`**: `__repr__`/`__str__` de `ReauthMaterial` redactado
  (`<ReauthMaterial redacted>`), evita fuga en logs.
- **`test_protected_credential_never_persists_plaintext_password`**: el repositorio nunca persiste el
  password en claro.

Guard de arranque (`backend/tests/test_jwt_startup.py`, preexistente, se mantiene verde):

- El arranque del servicio web exige un `JWT_SECRET` no-default (NFR1.1); un secreto vacío/por
  defecto aborta el arranque.

## Cómo ejecutar

```bash
# desde backend/ — tests de seguridad de credenciales + guard de arranque
JWT_SECRET="ci-ephemeral-test-secret-not-production" \
  pytest tests/test_durable_session_service.py \
         tests/test_durable_session_repository.py \
         tests/test_jwt_startup.py -q
```

## SAST / escaneo de secretos (gate de CI, no de esta etapa local)

- **gitleaks** es **gate bloqueante en CI** (`.github/workflows/ci.yml`) y corre sobre el diff del MR.
  No se ejecuta en esta etapa local (no instalado en el entorno de desarrollo); su verificación es
  responsabilidad del pipeline. **Diferido a: CI (gate de MR)**. Evidencia esperada: job de gitleaks
  verde en el MR.
- **ruff** con la familia `S` (flake8-bandit) es advisory hoy; no bloquea.

## Objetivos

- 0 apariciones de la contraseña en claro en cualquier estado persistido (verificado por test).
- Guard `JWT_SECRET` no-default activo (verificado por test).
- gitleaks verde en el gate de MR antes de fusionar (diferido a CI).
