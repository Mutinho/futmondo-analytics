import { Component, inject, signal, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';

interface PrizeRound {
  matchday: number;
  ranking_prize: number;
  mvp_prize: number;
  position: number;
  total: number;
}

@Component({
  selector: 'app-prizes-dialog',
  standalone: true,
  imports: [MatDialogModule, MatTableModule, MatProgressSpinnerModule, MatButtonModule, MoneyPipe],
  template: `
    <h2 mat-dialog-title>🏆 Premios — {{ data.team_name }}</h2>
    <mat-dialog-content>
      @if (loading()) {
        <div class="loading"><mat-spinner diameter="32" /></div>
      } @else if (rounds().length === 0) {
        <p class="empty">No hay premios registrados.</p>
      } @else {
        <table mat-table [dataSource]="rounds()">
          <ng-container matColumnDef="matchday">
            <th mat-header-cell *matHeaderCellDef>Jornada</th>
            <td mat-cell *matCellDef="let r">J{{ r.matchday }}</td>
          </ng-container>
          <ng-container matColumnDef="position">
            <th mat-header-cell *matHeaderCellDef>Posición</th>
            <td mat-cell *matCellDef="let r">{{ r.position }}º</td>
          </ng-container>
          <ng-container matColumnDef="ranking_prize">
            <th mat-header-cell *matHeaderCellDef>Ranking</th>
            <td mat-cell *matCellDef="let r">{{ r.ranking_prize | money }}</td>
          </ng-container>
          <ng-container matColumnDef="mvp_prize">
            <th mat-header-cell *matHeaderCellDef>MVP</th>
            <td mat-cell *matCellDef="let r">
              @if (r.mvp_prize > 0) { {{ r.mvp_prize | money }} } @else { - }
            </td>
          </ng-container>
          <ng-container matColumnDef="total">
            <th mat-header-cell *matHeaderCellDef>Total</th>
            <td mat-cell *matCellDef="let r"><strong>{{ r.total | money }}</strong></td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
        <div class="total-row">
          <span>Total acumulado:</span>
          <strong>{{ totalPrizes() | money }}</strong>
        </div>
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cerrar</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .loading { display: flex; justify-content: center; padding: 40px; }
    .empty { text-align: center; color: var(--mat-sys-on-surface-variant); padding: 20px; }
    table { width: 100%; }
    .total-row {
      display: flex; justify-content: space-between; align-items: center;
      padding: 16px 0 8px; border-top: 2px solid var(--mat-sys-outline-variant);
      margin-top: 12px; font-size: 1.1em;
    }
  `]
})
export class PrizesDialogComponent implements OnInit {
  data = inject<{ team_id: string; team_name: string; championship_id: string }>(MAT_DIALOG_DATA);
  private http = inject(HttpClient);

  loading = signal(true);
  rounds = signal<PrizeRound[]>([]);
  totalPrizes = signal(0);
  columns = ['matchday', 'position', 'ranking_prize', 'mvp_prize', 'total'];

  async ngOnInit() {
    try {
      const params = new HttpParams().set('championship_id', this.data.championship_id);
      const resp = await firstValueFrom(
        this.http.get<any>(`/api/v1/analytics/prizes/${this.data.team_id}`, { params })
      );
      this.rounds.set(resp.rounds || []);
      this.totalPrizes.set(resp.total_prizes || 0);
    } catch { }
    this.loading.set(false);
  }
}
