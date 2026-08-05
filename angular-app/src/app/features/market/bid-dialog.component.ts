import { Component, inject, signal, computed } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { MoneyPipe } from '../../shared/pipes/money.pipe';

export interface BidDialogData {
  playerName: string;
  team: string;
  suggestedBid: number;
  marketPrice: number;
  maxBid: number;
}

export interface BidDialogResult {
  confirmed: boolean;
  price: number;
}

@Component({
  selector: 'app-bid-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatIconModule, FormsModule, MoneyPipe],
  template: `
    <h2 mat-dialog-title>🔨 Pujar por {{ data.playerName }}</h2>
    <mat-dialog-content>

      <div class="limits">
        <div class="limit-item">
          <span class="limit-label">Valor de mercado (mín)</span>
          <span class="limit-value">{{ data.marketPrice | money }}</span>
        </div>
        <div class="limit-item">
          <span class="limit-label">Puja máxima permitida</span>
          <span class="limit-value max">{{ data.maxBid | money }}</span>
        </div>
      </div>

      <mat-form-field appearance="outline" class="bid-field">
        <mat-label>Cantidad a pujar</mat-label>
        <input matInput type="number"
               [(ngModel)]="bidAmount"
               [min]="data.marketPrice"
               [max]="data.maxBid"
               (ngModelChange)="onAmountChange()">
        <span matTextPrefix>€&nbsp;</span>
      </mat-form-field>

      @if (validationError()) {
        <p class="validation-error">{{ validationError() }}</p>
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancel()">Cancelar</button>
      <button mat-flat-button color="primary" [disabled]="!isValid()" (click)="confirm()">
        <mat-icon>gavel</mat-icon>
        Pujar
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .player-info { color: var(--mat-sys-on-surface-variant); margin: -8px 0 16px; }
    .limits { display: flex; gap: 24px; margin-bottom: 20px; padding: 12px 16px; background: var(--mat-sys-surface-container); border-radius: 8px; }
    .limit-item { display: flex; flex-direction: column; gap: 2px; }
    .limit-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--mat-sys-on-surface-variant); font-weight: 600; }
    .limit-value { font-size: 1.1em; font-weight: 700; }
    .limit-value.max { color: #1565c0; }
    .bid-field { width: 100%; }
    .validation-error { color: #d32f2f; font-size: 0.85em; margin-top: -8px; }
    mat-dialog-content { min-width: 350px; }
  `]
})
export class BidDialogComponent {
  data: BidDialogData = inject(MAT_DIALOG_DATA);
  private dialogRef = inject(MatDialogRef<BidDialogComponent>);

  bidAmount = this.data.suggestedBid;
  validationError = signal('');

  onAmountChange() {
    this.validate();
  }

  validate(): boolean {
    if (!this.bidAmount || this.bidAmount <= 0) {
      this.validationError.set('La cantidad debe ser mayor que 0');
      return false;
    }
    if (this.bidAmount < this.data.marketPrice) {
      this.validationError.set(`Mínimo: ${this.formatMoney(this.data.marketPrice)} (valor de mercado)`);
      return false;
    }
    if (this.bidAmount > this.data.maxBid) {
      this.validationError.set(`Máximo: ${this.formatMoney(this.data.maxBid)} (puja máxima permitida)`);
      return false;
    }
    this.validationError.set('');
    return true;
  }

  isValid(): boolean {
    return !!this.bidAmount &&
      this.bidAmount >= this.data.marketPrice &&
      this.bidAmount <= this.data.maxBid;
  }

  confirm() {
    if (!this.isValid()) return;
    this.dialogRef.close({ confirmed: true, price: this.bidAmount } as BidDialogResult);
  }

  cancel() {
    this.dialogRef.close({ confirmed: false, price: 0 } as BidDialogResult);
  }

  private formatMoney(value: number): string {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(value);
  }
}
