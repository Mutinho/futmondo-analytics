import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-splash',
  standalone: true,
  imports: [MatProgressSpinnerModule],
  template: `
    <div class="splash">
      <img src="icon.svg" alt="Futmondo" class="logo" />
      <mat-spinner diameter="40" color="accent" />
    </div>
  `,
  styles: [`
    .splash {
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      height: 100vh; gap: 24px;
      background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #43a047 100%);
    }
    .logo { width: 80px; height: 80px; }
    mat-spinner { --mdc-circular-progress-active-indicator-color: #fff; }
  `]
})
export class SplashComponent implements OnInit {
  private router = inject(Router);
  private authService = inject(AuthService);

  async ngOnInit() {
    // Save the intended URL (what the user had before F5)
    const intendedUrl = localStorage.getItem('futmondo_last_route') || '/budget';
    
    // Try to recover session from HttpOnly cookie
    const recovered = await this.authService.tryRecoverSession();
    
    if (recovered) {
      this.router.navigateByUrl(intendedUrl, { replaceUrl: true });
    } else {
      this.router.navigate(['/login'], { replaceUrl: true });
    }
  }
}
