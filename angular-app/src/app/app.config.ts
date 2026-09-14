import { ApplicationConfig, provideBrowserGlobalErrorListeners, isDevMode } from '@angular/core';
import { provideRouter, withPreloading } from '@angular/router';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideServiceWorker } from '@angular/service-worker';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { IdlePreloadingStrategy } from './core/preloading/idle-preloading-strategy';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // Precarga diferida por inactividad en lugar de PreloadAllModules: mantiene
    // la precarga de rutas lazy pero fuera de la ventana crítica de arranque
    // (FR3, NFR4). La estrategia es un provider inyectable.
    provideRouter(routes, withPreloading(IdlePreloadingStrategy)),
    provideAnimationsAsync(),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideServiceWorker('ngsw-worker.js', {
      enabled: !isDevMode(),
      registrationStrategy: 'registerWhenStable:30000'
    }),
  ]
};
