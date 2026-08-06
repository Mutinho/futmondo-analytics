import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  email: string;
  display_name?: string;
}

interface RefreshResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

const STORAGE_KEYS = {
  accessToken: 'futmondo_access_token',
  refreshToken: 'futmondo_refresh_token',
  user: 'futmondo_user',
};

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private _user = signal<{ user_id: string; email: string; display_name?: string } | null>(
    this.loadUser()
  );

  /** Current authenticated user (null if not logged in) */
  user = this._user.asReadonly();

  /** Whether the user is authenticated */
  isAuthenticated = computed(() => !!this._user() && !!this.getAccessToken());

  /** Login with Futmondo credentials */
  async login(email: string, password: string): Promise<void> {
    const response = await firstValueFrom(
      this.http.post<TokenResponse>('/auth/login', { email, password })
    );

    this.saveTokens(response.access_token, response.refresh_token);
    const user = {
      user_id: response.user_id,
      email: response.email,
      display_name: response.display_name,
    };
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
    this._user.set(user);
  }

  /** Refresh the access token using the stored refresh token */
  async refresh(): Promise<string | null> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return null;

    try {
      const response = await firstValueFrom(
        this.http.post<RefreshResponse>('/auth/refresh', { refresh_token: refreshToken })
      );
      localStorage.setItem(STORAGE_KEYS.accessToken, response.access_token);
      return response.access_token;
    } catch {
      // Refresh failed — force logout
      this.clearSession();
      return null;
    }
  }

  /** Logout — revoke refresh token and clear local state */
  async logout(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    if (refreshToken) {
      try {
        await firstValueFrom(
          this.http.post('/auth/logout', { refresh_token: refreshToken })
        );
      } catch {
        // Server-side revoke failed — still clear locally
      }
    }
    this.clearSession();
    this.router.navigate(['/login']);
  }

  /** Get the current access token */
  getAccessToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.accessToken);
  }

  /** Get the current refresh token */
  getRefreshToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.refreshToken);
  }

  private saveTokens(access: string, refresh: string): void {
    localStorage.setItem(STORAGE_KEYS.accessToken, access);
    localStorage.setItem(STORAGE_KEYS.refreshToken, refresh);
  }

  private clearSession(): void {
    localStorage.removeItem(STORAGE_KEYS.accessToken);
    localStorage.removeItem(STORAGE_KEYS.refreshToken);
    localStorage.removeItem(STORAGE_KEYS.user);
    this._user.set(null);
  }

  private loadUser(): { user_id: string; email: string; display_name?: string } | null {
    const stored = localStorage.getItem(STORAGE_KEYS.user);
    if (!stored) return null;
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  }
}
