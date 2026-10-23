import Foundation

/// Pure, deterministic money math for the Calculadora (FR7 / BR1–BR4). All
/// functions are side-effect-free and `UIKit`/`SwiftUI`-free, so they are
/// fully covered by `swift test` on Linux/WSL.
///
/// The money invariants (FR7) are the acceptance criteria of the screen; they
/// live here, not in the view model, so they can be unit-tested directly.
public enum CalculatorMath {
    /// Projected value of a player `daysAhead` days from now (BR1.1):
    /// `value + (change ?? 0) * daysAhead`. A `nil` trend counts as 0, and a
    /// negative `daysAhead` is clamped to 0 (the picker already bounds it, but
    /// the math stays safe, BR1.2).
    public static func projectedValue(_ player: RosterPlayer, daysAhead: Int) -> Int {
        let days = max(0, daysAhead)
        return player.value + (player.change ?? 0) * days
    }

    /// `selectedTotal` (BR2.1): the sum of the projected value of every
    /// `players` row whose id is in `selectedIds`.
    public static func selectedTotal(
        players: [RosterPlayer],
        selectedIds: Set<String>,
        daysAhead: Int
    ) -> Int {
        players
            .filter { selectedIds.contains($0.playerId) }
            .reduce(0) { $0 + projectedValue($1, daysAhead: daysAhead) }
    }

    /// `onSaleTotal` (BR2.2): the sum of `value` over the on-sale players. The
    /// on-sale value is NOT projected — it is the committed sale value.
    public static func onSaleTotal(_ onSale: [OnSalePlayer]) -> Int {
        onSale.reduce(0) { $0 + $1.value }
    }

    /// `futureBalance` (BR3.1 / BR3.2):
    /// `balance + selectedTotal + (includeOnSale ? onSaleTotal : 0) -
    /// activeBidsTotal`. `activeBidsTotal` is ALWAYS subtracted, with the toggle
    /// ON or OFF (BR3.2). `profit` is never part of this (BR7.1 / R-03).
    public static func futureBalance(
        balance: Int,
        selectedTotal: Int,
        onSaleTotal: Int,
        includeOnSale: Bool,
        activeBidsTotal: Int
    ) -> Int {
        balance
            + selectedTotal
            + (includeOnSale ? onSaleTotal : 0)
            - activeBidsTotal
    }
}
