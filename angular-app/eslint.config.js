// Configuración base de ESLint para Angular (flat config).
//
// Escalonado (Code Style afirmado + R-05): arranca en modo TOLERANTE (advisory).
// El gate de CI ejecuta ESLint en modo advisory (continue-on-error) en esta
// fase; se pasará a bloqueante en un trabajo posterior. Requiere instalar
// `angular-eslint`, `@typescript-eslint/*` y `eslint` como devDependencies
// (se añaden al adoptar el gate bloqueante para no ampliar la superficie ahora).
//
// @ts-check
const eslint = require('@eslint/js');
const tseslint = require('typescript-eslint');
const angular = require('angular-eslint');

module.exports = tseslint.config(
  {
    files: ['**/*.ts'],
    ignores: ['.angular/**', 'dist/**', 'node_modules/**'],
    extends: [
      eslint.configs.recommended,
      ...tseslint.configs.recommended,
      ...angular.configs.tsRecommended,
    ],
    processor: angular.processInlineTemplates,
    rules: {
      '@angular-eslint/directive-selector': [
        'warn',
        { type: 'attribute', prefix: 'app', style: 'camelCase' },
      ],
      '@angular-eslint/component-selector': [
        'warn',
        { type: 'element', prefix: 'app', style: 'kebab-case' },
      ],
      // Base heredada: degradar a warn para el escalonado advisory.
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': 'warn',
    },
  },
  {
    files: ['**/*.html'],
    extends: [
      ...angular.configs.templateRecommended,
      ...angular.configs.templateAccessibility,
    ],
    rules: {},
  },
);
