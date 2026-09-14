// Configuración de Karma para el runner de tests de Angular.
//
// R-06: se define un launcher `ChromeHeadlessNoSandbox` (Chrome headless con
// `--no-sandbox`) para runners containerizados (CI), donde el sandbox de Chrome
// no está disponible. Comando unit-scoped:
//   npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox
//
// Requisito de entorno: Chrome/Chromium disponible en PATH (o CHROME_BIN).
module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
    ],
    client: {
      jasmine: {},
      clearContext: false,
    },
    jasmineHtmlReporter: {
      suppressAll: true,
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage/angular-app'),
      subdir: '.',
      reporters: [{ type: 'html' }, { type: 'text-summary' }],
    },
    reporters: ['progress', 'kjhtml'],
    browsers: ['ChromeHeadlessNoSandbox'],
    customLaunchers: {
      // Launcher headless sin sandbox para CI containerizado (R-06).
      ChromeHeadlessNoSandbox: {
        base: 'ChromeHeadless',
        flags: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
      },
    },
    restartOnFileChange: true,
    singleRun: false,
  });
};
