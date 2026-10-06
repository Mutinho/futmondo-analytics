import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';

import { CalculatorComponent } from './calculator.component';
import { ChampionshipService } from '../../core/services/championship.service';
import { RosterService } from '../../core/services/roster.service';

/**
 * Specs for `CalculatorComponent` — calculator-toggle unit.
 *
 * Characterization-first (NFR4): freezes the current `futureBalance` formula
 * (equivalent to the toggle being ON) before asserting the new conditional
 * behaviour. The later specs assert the EFFECT of the toggle on the computed
 * value and on localStorage persistence/restore — not mirror tests.
 *
 * HTTP services are stubbed so the constructor effect never hits the network:
 * `ChampionshipService.activeId()` returns '' (falsy), so `loadData()` is never
 * invoked and the production signals keep their test-seeded values.
 */

const STORAGE_KEY = 'futmondo_calc_include_onsale';

const ON_SALE_PLAYERS = [
  { player_id: 'p1', value: 30 },
  { player_id: 'p2', value: 20 },
]; // onSaleTotal = 50

/** Full roster: two on-sale players (p1, p2) plus one regular player (p3). */
const ROSTER_PLAYERS = [
  { player_id: 'p1', name: 'OnSale One', value: 30, change: 0 },
  { player_id: 'p2', name: 'OnSale Two', value: 20, change: 0 },
  { player_id: 'p3', name: 'Regular', value: 10, change: 0 },
];

function setup() {
  const championshipStub = { activeId: signal('') };
  const rosterStub = {
    getMyRoster: vi.fn(),
    getOnSale: vi.fn(),
    sell: vi.fn(),
    cancelSale: vi.fn(),
  };
  const httpStub = { get: vi.fn() };

  TestBed.configureTestingModule({
    providers: [
      { provide: ChampionshipService, useValue: championshipStub },
      { provide: RosterService, useValue: rosterStub },
      { provide: HttpClient, useValue: httpStub },
    ],
  });

  const fixture = TestBed.createComponent(CalculatorComponent);
  const component = fixture.componentInstance;
  return { component, fixture, championshipStub, rosterStub, httpStub };
}

/** Seed the read-only market/roster signals used by futureBalance. */
function seedBalances(component: CalculatorComponent) {
  component.balance.set(100);
  component.activeBidsTotal.set(40);
  component.onSalePlayers.set(ON_SALE_PLAYERS as any);
  // No players selected → selectedTotal() = 0.
  component.players.set([]);
  component.selectedIds.set({});
}

/**
 * Drive the real `loadData()` with stubbed services so the private rawRoster /
 * onSaleIds state is populated and `rebuildSelectable()` composes the selectable
 * list the same way production does. Lets FR5 specs assert the EFFECT on the
 * selectable list (players()/dataSource.data) rather than reaching into privates.
 */
async function loadWith(
  component: CalculatorComponent,
  rosterStub: any,
  httpStub: any,
) {
  rosterStub.getMyRoster.mockResolvedValue({ players: ROSTER_PLAYERS });
  rosterStub.getOnSale.mockResolvedValue({ players: ON_SALE_PLAYERS });
  httpStub.get.mockReturnValue(
    of({ user_info: { balance: 100, active_bids_total: 40, active_bids_count: 1 } }),
  );
  await component.loadData();
}

describe('CalculatorComponent — calculator-toggle', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.resetTestingModule();
  });

  // --- Step 2: characterization of current (ON-equivalent) behaviour ---
  it('congela el futureBalance actual: balance + selectedTotal + onSaleTotal - activeBidsTotal (ON por defecto)', () => {
    const { component } = setup();
    seedBalances(component);
    // Default (no stored value) → includeOnSale ON (BR3.3).
    expect(component.includeOnSale()).toBe(true);
    // 100 + 0 + 50 - 40 = 110
    expect(component.futureBalance()).toBe(110);
  });

  // --- Step 5a: ON includes onSaleTotal (FR1.2/BR1.1) ---
  it('con el toggle ON incluye onSaleTotal en futureBalance', () => {
    const { component } = setup();
    seedBalances(component);
    component.setIncludeOnSale(true);
    // 100 + 0 + 50 - 40 = 110
    expect(component.futureBalance()).toBe(110);
  });

  // --- Step 5b: OFF excludes onSaleTotal (FR1.3/BR1.2) ---
  it('con el toggle OFF excluye onSaleTotal de futureBalance', () => {
    const { component } = setup();
    seedBalances(component);
    component.setIncludeOnSale(false);
    // 100 + 0 + 0 - 40 = 60
    expect(component.futureBalance()).toBe(60);
  });

  // --- Step 5c: activeBidsTotal subtracts in both states (FR2.1/BR2.1) ---
  it('activeBidsTotal siempre resta, tanto en ON como en OFF (invariante)', () => {
    const { component } = setup();
    seedBalances(component);

    component.setIncludeOnSale(true);
    const futureOn = component.futureBalance(); // 110
    component.setIncludeOnSale(false);
    const futureOff = component.futureBalance(); // 60

    // The only difference between ON and OFF is onSaleTotal (50); the active
    // bids (40) are subtracted from both.
    expect(futureOn - futureOff).toBe(50);
    expect(futureOn).toBe(100 + 50 - 40);
    expect(futureOff).toBe(100 - 40);
  });

  // --- Step 5d: toggling persists to localStorage (FR3.1/BR3.1) ---
  it('cambiar el toggle persiste el valor en localStorage', () => {
    const { component } = setup();
    component.setIncludeOnSale(false);
    expect(localStorage.getItem(STORAGE_KEY)).toBe('false');
    component.setIncludeOnSale(true);
    expect(localStorage.getItem(STORAGE_KEY)).toBe('true');
  });

  // --- Step 5e: restore from localStorage and fallback to ON ---
  it("restaura ON cuando localStorage = 'true' (FR3.2/BR3.2)", () => {
    localStorage.setItem(STORAGE_KEY, 'true');
    const { component } = setup();
    expect(component.includeOnSale()).toBe(true);
  });

  it("restaura OFF cuando localStorage = 'false' (FR3.2/BR3.2)", () => {
    localStorage.setItem(STORAGE_KEY, 'false');
    const { component } = setup();
    expect(component.includeOnSale()).toBe(false);
  });

  it('fallback a ON cuando la clave está ausente (FR3.3/BR3.3)', () => {
    // localStorage cleared in beforeEach → key absent.
    const { component } = setup();
    expect(component.includeOnSale()).toBe(true);
  });

  it('fallback a ON ante un valor corrupto/no booleano (FR3.4/BR3.4)', () => {
    localStorage.setItem(STORAGE_KEY, 'maybe');
    const { component } = setup();
    expect(component.includeOnSale()).toBe(true);
  });

  // --- FR5: selectable-list composition conditional on the toggle ---

  it('con ON excluye los jugadores en venta de la lista seleccionable (FR5.1/BR5.1)', async () => {
    localStorage.setItem(STORAGE_KEY, 'true');
    const { component, rosterStub, httpStub } = setup();
    await loadWith(component, rosterStub, httpStub);

    const ids = component.players().map(p => p.player_id);
    expect(ids).toEqual(['p3']); // on-sale p1/p2 excluded
    expect(component.dataSource.data.map(p => p.player_id)).toEqual(['p3']);
    // onSaleTotal still contributes to futureBalance under ON (BR1.1).
    // 100 + 0 (selected) + 50 (onSale) - 40 (bids) = 110
    expect(component.futureBalance()).toBe(110);
  });

  it('con OFF incluye los jugadores en venta en la lista, deseleccionados, y excluye onSaleTotal (FR5.2/FR5.3/BR5.2)', async () => {
    localStorage.setItem(STORAGE_KEY, 'false');
    const { component, rosterStub, httpStub } = setup();
    await loadWith(component, rosterStub, httpStub);

    const ids = component.players().map(p => p.player_id);
    expect(ids).toEqual(['p1', 'p2', 'p3']); // full roster
    // The on-sale players entered DESELECTED (BR5.2).
    expect(component.selectedIds()).toEqual({});
    // onSaleTotal excluded under OFF (BR1.2): 100 + 0 - 40 = 60
    expect(component.futureBalance()).toBe(60);
  });

  it('invariante anti-doble-conteo: con OFF, seleccionar un ex-onSale suma a selectedTotal una sola vez (FR5.5/BR5.4)', async () => {
    localStorage.setItem(STORAGE_KEY, 'false');
    const { component, rosterStub, httpStub } = setup();
    await loadWith(component, rosterStub, httpStub);

    const p1 = component.players().find(p => p.player_id === 'p1')!;
    component.togglePlayer(p1, true);

    // p1 (value 30) counts via selectedTotal ONLY (onSaleTotal excluded under OFF).
    // 100 + 30 - 40 = 90 — p1 is NOT double-counted.
    expect(component.selectedTotal()).toBe(30);
    expect(component.futureBalance()).toBe(90);
  });

  it('transición OFF→ON re-excluye los jugadores en venta y limpia su selección manual (FR5.4/BR5.3)', async () => {
    localStorage.setItem(STORAGE_KEY, 'false');
    const { component, rosterStub, httpStub } = setup();
    await loadWith(component, rosterStub, httpStub);

    // Manually select an on-sale player under OFF.
    const p1 = component.players().find(p => p.player_id === 'p1')!;
    component.togglePlayer(p1, true);
    expect(component.selectedIds()['p1']).toBe(true);

    // Flip to ON.
    component.setIncludeOnSale(true);

    // p1/p2 are re-excluded from the list and p1's manual selection is dropped.
    expect(component.players().map(p => p.player_id)).toEqual(['p3']);
    expect(component.selectedIds()['p1']).toBeUndefined();
    // p1's value now counts via onSaleTotal only: 100 + 0 + 50 - 40 = 110
    expect(component.futureBalance()).toBe(110);
  });
});
