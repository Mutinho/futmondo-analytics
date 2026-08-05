import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { AnalyticsService } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics-classification',
  standalone: true,
  imports: [MatProgressSpinnerModule, MatTableModule, MatButtonModule, FormsModule, MatInputModule, MatFormFieldModule],
  template: `
    <h3>🏆 Clasificación Dinámica</h3>
    <p class="section-desc">Clasificación filtrable por las últimas N jornadas. Permite ver quién está en mejor forma reciente, independientemente del acumulado total.</p>
    <div class="controls">
      <mat-form-field appearance="outline" class="window-field">
        <mat-label>Últimas jornadas</mat-label>
        <input matInput type="number" [(ngModel)]="window" min="1" max="38">
      </mat-form-field>
      <button mat-raised-button color="primary" (click)="load()">Aplicar</button>
    </div>

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> Cargando clasificación...</div>
    } @else if (!hasData()) {
      <div class="empty">🏆 No hay datos de clasificación disponibles.</div>
    } @else {
      <div class="table-container">
        <table mat-table [dataSource]="classification()">
          <ng-container matColumnDef="position">
            <th mat-header-cell *matHeaderCellDef>#</th>
            <td mat-cell *matCellDef="let t; let i = index">{{ i + 1 }}</td>
          </ng-container>
          <ng-container matColumnDef="team_name">
            <th mat-header-cell *matHeaderCellDef>Equipo</th>
            <td mat-cell *matCellDef="let t"><strong>{{ t.team_name }}</strong></td>
          </ng-container>
          <ng-container matColumnDef="points">
            <th mat-header-cell *matHeaderCellDef>Puntos</th>
            <td mat-cell *matCellDef="let t">{{ t.points }}</td>
          </ng-container>
          <ng-container matColumnDef="average">
            <th mat-header-cell *matHeaderCellDef>Media</th>
            <td mat-cell *matCellDef="let t">{{ t.average?.toFixed(1) }}</td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`
    .controls { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
    .window-field { width: 150px; }
    .loading { display: flex; align-items: center; gap: 12px; padding: 32px; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 48px; color: var(--mat-sys-on-surface-variant); }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .section-desc { color: #666666; font-size: 13px; margin: -4px 0 20px; }
  `]
})
export class ClassificationComponent {
  private analyticsService = inject(AnalyticsService);
  loading = signal(true);
  hasData = signal(false);
  classification = signal<any[]>([]);
  columns = ['position', 'team_name', 'points', 'average'];
  window = 5;

  constructor() { this.load(); }

  async load() {
    this.loading.set(true);
    try {
      const data = await this.analyticsService.getCustomClassification(this.window);
      const teams = data?.classification || data?.teams || [];
      this.classification.set(teams);
      this.hasData.set(teams.length > 0);
    } catch { this.hasData.set(false); }
    finally { this.loading.set(false); }
  }
}
