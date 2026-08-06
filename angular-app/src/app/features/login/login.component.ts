import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    FormsModule, MatCardModule, MatFormFieldModule, MatInputModule,
    MatButtonModule, MatIconModule, MatProgressSpinnerModule
  ],
  template: `
    <div class="login-wrapper">
      <mat-card class="login-card">
        <div class="login-header">
          <img src="icon.svg" alt="Futmondo" class="logo" />
          <h1>Futmondo Analytics</h1>
          <p class="subtitle">Inicia sesión con tu cuenta de Futmondo</p>
        </div>

        <mat-card-content>
          <form (ngSubmit)="onSubmit()" class="login-form">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Email</mat-label>
              <input matInput type="email" [(ngModel)]="email" name="email"
                     placeholder="tu@email.com" required [disabled]="loading()" />
              <mat-icon matPrefix>email</mat-icon>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Contraseña</mat-label>
              <input matInput [type]="hidePassword ? 'password' : 'text'"
                     [(ngModel)]="password" name="password"
                     required [disabled]="loading()" />
              <mat-icon matPrefix>lock</mat-icon>
              <button mat-icon-button matSuffix type="button"
                      (click)="hidePassword = !hidePassword">
                <mat-icon>{{ hidePassword ? 'visibility_off' : 'visibility' }}</mat-icon>
              </button>
            </mat-form-field>

            @if (error()) {
              <div class="error-message">
                <mat-icon>error</mat-icon>
                <span>{{ error() }}</span>
              </div>
            }

            <button mat-flat-button color="primary" type="submit" class="login-btn"
                    [disabled]="loading() || !email || !password">
              @if (loading()) {
                <mat-spinner diameter="20" />
              } @else {
                Iniciar sesión
              }
            </button>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .login-wrapper {
      display: flex; align-items: center; justify-content: center;
      min-height: 100vh; padding: 16px;
      background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #43a047 100%);
    }
    .login-card {
      width: 100%; max-width: 400px; padding: 40px 32px;
      border-radius: 16px;
    }
    .login-header {
      text-align: center; margin-bottom: 32px;
    }
    .logo {
      width: 64px; height: 64px; margin-bottom: 16px;
    }
    .login-header h1 {
      margin: 0; font-size: 1.5em; font-weight: 700;
      color: var(--mat-sys-on-surface);
    }
    .subtitle {
      margin: 8px 0 0; font-size: 0.9em;
      color: var(--mat-sys-on-surface-variant);
    }
    .login-form {
      display: flex; flex-direction: column; gap: 4px;
    }
    .full-width { width: 100%; }
    .login-btn {
      width: 100%; height: 48px; font-size: 1em; font-weight: 600;
      margin-top: 8px;
    }
    .login-btn mat-spinner { display: inline-block; }
    .error-message {
      display: flex; align-items: center; gap: 8px;
      padding: 12px; border-radius: 8px;
      background: #ffebee; color: #d32f2f;
      font-size: 0.85em; margin-bottom: 8px;
    }
    .error-message mat-icon { font-size: 18px; width: 18px; height: 18px; }
  `]
})
export class LoginComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  hidePassword = true;
  loading = signal(false);
  error = signal('');

  async onSubmit() {
    if (!this.email || !this.password) return;

    this.loading.set(true);
    this.error.set('');

    try {
      await this.authService.login(this.email, this.password);
      this.router.navigate(['/']);
    } catch (err: any) {
      const detail = err?.error?.detail || err?.message || 'Error al iniciar sesión';
      this.error.set(detail);
    } finally {
      this.loading.set(false);
    }
  }
}
