# Instrucciones de Test de Integración

## Aplicabilidad
No aplican en este intent: scope `bugfix`, Test Strategy `Minimal`. El arreglo
se limita a un fichero de test unitario/caracterización de `AnalyticsService`;
no hay nuevas interacciones cross-unit que requieran tests de integración.

## Cobertura existente
La suite de caracterización del backend (pytest) ya cubre el comportamiento
integrado relevante y permanece en verde (54 passed). Cualquier verificación
de integración adicional se delega al pipeline de CI (`fly-deploy.yml`).
