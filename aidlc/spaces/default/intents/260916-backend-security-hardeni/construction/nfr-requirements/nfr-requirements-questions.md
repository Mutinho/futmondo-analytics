# Preguntas de Requisitos No Funcionales — Backend Security Hardening

> Scope `security-patch` (Minimal), intent sin DAG de unidades. Los NFR se derivan de
> los requisitos aprobados (`requirements.md`, NFR1-5) y de la base de código.

## Q1 — Método de elaboración de los NFR

Dado el scope acotado de seguridad y que los cinco requisitos ya están aprobados, ¿cómo elaboramos los NFR?

- A. Derivar los NFR directamente de los requisitos aprobados y la base de código (sin abrir preguntas nuevas de targets).
- B. Abrir preguntas explícitas de NFR (targets concretos: rate-limiting, umbrales, etc.) antes de generar.
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Resumen de las decisiones de NFR (derivadas de los requisitos aprobados):

- Seguridad: no-regresión de auth/JWT (NFR1.1, NFR1.2); refresh token naive/aware correcto (NFR1.3, FR9); validación de `price` en el backend → 422 (NFR2.1, FR6); superficie de fotos documentada, pública intencionada (NFR3.1, FR7); verificación TLS activa, flag `SSL_VERIFY` eliminado (NFR4.1, FR8); guarda `ENABLE_DB_ADMIN` con test (NFR5.1, FR18); sin password en claro (NFR3.2).
- Rendimiento: sin regresión; validaciones en memoria, sin llamadas de red nuevas.
- Escalabilidad: sin cambios de topología (Fly.io min=max=1, Neon free), coste 0 €.
- Fiabilidad: suite existente en verde (gate bloqueante); un test por FR cubriendo el camino de error; FR9 actualiza los tests de caracterización.
- Observabilidad: adaptada a Fly.io/coste 0 € (`fly logs`, healthcheck); SLO formales con burn-rate NO-APLICA.
- Stack: sin tecnología nueva; se usan librerías ya presentes.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
