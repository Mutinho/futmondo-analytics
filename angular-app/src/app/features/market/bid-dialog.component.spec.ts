import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import {
  BidDialogComponent,
  type BidDialogData,
  type BidDialogResult,
} from './bid-dialog.component';

/**
 * Seeded spec for `BidDialogComponent` (FR10.3.2 — high-value standalone
 * component with signals). Freezes the bid-bounds validation (min = market
 * price, max = allowed max bid) and the dialog close contract. Validates the
 * signal-backed `validationError` and the `confirm`/`cancel` results.
 */
const DATA: BidDialogData = {
  playerName: 'Jugador Uno',
  team: 'Equipo A',
  suggestedBid: 150,
  marketPrice: 100,
  maxBid: 200,
};

function setup(data: Partial<BidDialogData> = {}) {
  const dialogRef = { close: vi.fn() };
  TestBed.configureTestingModule({
    providers: [
      { provide: MAT_DIALOG_DATA, useValue: { ...DATA, ...data } },
      { provide: MatDialogRef, useValue: dialogRef },
    ],
  });
  const fixture = TestBed.createComponent(BidDialogComponent);
  return { component: fixture.componentInstance, dialogRef };
}

describe('BidDialogComponent', () => {
  beforeEach(() => TestBed.resetTestingModule());

  it('arranca con la puja sugerida y es valida dentro de los limites', () => {
    const { component } = setup();
    expect(component.bidAmount).toBe(150);
    expect(component.isValid()).toBe(true);
    expect(component.validationError()).toBe('');
  });

  it('marca error cuando la puja es menor que el valor de mercado', () => {
    const { component } = setup();
    component.bidAmount = 50;
    component.onAmountChange();
    expect(component.isValid()).toBe(false);
    expect(component.validationError()).toContain('Mínimo');
  });

  it('marca error cuando la puja supera la puja maxima permitida', () => {
    const { component } = setup();
    component.bidAmount = 500;
    component.onAmountChange();
    expect(component.isValid()).toBe(false);
    expect(component.validationError()).toContain('Máximo');
  });

  it('marca error cuando la puja es 0 o negativa', () => {
    const { component } = setup();
    component.bidAmount = 0;
    expect(component.validate()).toBe(false);
    expect(component.validationError()).toContain('mayor que 0');
  });

  it('confirm cierra el dialogo con el precio cuando es valido', () => {
    const { component, dialogRef } = setup();
    component.bidAmount = 180;
    component.confirm();
    expect(dialogRef.close).toHaveBeenCalledWith({
      confirmed: true,
      price: 180,
    } as BidDialogResult);
  });

  it('confirm no cierra cuando la puja es invalida', () => {
    const { component, dialogRef } = setup();
    component.bidAmount = 5;
    component.confirm();
    expect(dialogRef.close).not.toHaveBeenCalled();
  });

  it('cancel cierra el dialogo con confirmed=false', () => {
    const { component, dialogRef } = setup();
    component.cancel();
    expect(dialogRef.close).toHaveBeenCalledWith({
      confirmed: false,
      price: 0,
    } as BidDialogResult);
  });
});
