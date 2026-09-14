# Instrucciones de Test de Seguridad

## Aplicabilidad
No aplican: scope `bugfix`, Test Strategy `Minimal`. El arreglo toca únicamente
un fichero de test; no altera autenticación, autorización ni superficie de ataque.

## Nota
El endurecimiento de seguridad existente (JWT fail-fast, gitleaks en CI, etc.)
permanece intacto. Sin acción para este intent.
