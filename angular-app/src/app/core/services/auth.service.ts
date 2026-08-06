import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

interface LoginResponse {
  access_token: string;
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

const USER_STORAGE_KEY = 'futmondo_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  /** Access token stored only in memory — never in localStorage */
  private accessToken: string | null = null;

  private _user = signal<{ user_id: string; email: string; display_name?: string } | null>(
    this.loadUser()
  );

  /** Whether initial session recovery has completed */
  private _initialized = signal(false);
  initialized = this._initialized.asReadonly();

  /** Current authenticated user (null if not logged in) */
  user = this._user.asReadonly();

  /** Whether the user is authenticated */
  isAuthenticated = computed(() => !!this._user() && !!this.accessToken);

  /** Login with Futmondo credentials */
  async login(email: string, password: string): Promise<void> {
    const response = await firstValueFrom(
      this.http.post<LoginResponse>('/auth/login', { email, password }, { withCredentials: true })
    );

    this.accessToken = response.access_token;
    const user = {
      user_id: response.user_id,
      email: response.email,
      display_name: response.display_name,
    };
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
    this._user.set(user);

    // Reset initialized so the effect in App re-fires after splash/tryRecoverSession
    this._initialized.set(false);
  }

  /** Refresh the access token using the HttpOnly cookie */
  async refresh(): Promise<string | null> {
    try {
      const response = await firstValueFrom(
        this.http.post<RefreshResponse>('/auth/refresh', {}, { withCredentials: true })
      );
      this.accessToken = response.access_token;
      return response.access_token;
    } catch {
      // Refresh failed — session expired
      this.clearSession();
      return null;
    }
  }

  /** Try to recover session on app startup (page refresh) */
  async tryRecoverSession(): Promise<boolean> {
    const user = this.loadUser();
    if (!user) {
      this._initialized.set(true);
      return false;
    }

    const token = await this.refresh();
    if (token) {
      this._user.set(user);
      this._initialized.set(true);
      return true;
    }

    this.clearSession();
    this._initialized.set(true);
    return false;
  }

  /** Logout — revoke refresh token cookie and clear local state */
  async logout(): Promise<void> {
    try {
      await firstValueFrom(
        this.http.post('/auth/logout', {}, { withCredentials: true })
      );
    } catch {
      // Server-side revoke failed — still clear locally
    }
    this.clearSession();
    this.router.navigate(['/login']);
  }

  /** Get the current access token (from memory) */
  getAccessToken(): string | null {
    return this.accessToken;
  }

  private clearSession(): void {
    this.accessToken = null;
    localStorage.removeItem(USER_STORAGE_KEY);
    this._user.set(null);
  }

  private loadUser(): { user_id: string; email: string; display_name?: string } | null {
    const stored = localStorage.getItem(USER_STORAGE_KEY);
    if (!stored) return null;
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  }
}
