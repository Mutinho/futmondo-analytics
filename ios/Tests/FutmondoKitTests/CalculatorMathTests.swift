import XCTest
@testable import FutmondoKit

final class CalculatorMathTests: XCTestCase {

    // MARK: - Fixtures

    private func player(
        _ id: String,
        value: Int,
        change: Int? = nil,
        profit: Int? = nil
    ) -> RosterPlayer {
        RosterPlayer(
            playerId: id,
            name: id,
            slug: id,
            team: "T",
            value: value,
            profit: profit,
            change: change
        )
    }

    private func onSale(_ id: String, value: Int) -> OnSalePlayer {
        OnSalePlayer(playerId: id, name: id, slug: id, value: value)
    }

    // MARK: - 1. projectedValue happy path (BR1.1)

    func testProjectedValueAddsTrendTimesDays() {
        let p = player("p1", value: 1_000_000, change: 50_000)
        XCTAssertEqual(CalculatorMath.projectedValue(p, daysAhead: 0), 1_000_000, "day 0 is current value")
        XCTAssertEqual(CalculatorMath.projectedValue(p, daysAhead: 3), 1_150_000, "value + 50k*3")
    }

    // MARK: - 2. projectedValue with nil change counts as 0 (BR1.1)

    func testProjectedValueNilChangeIsZeroTrend() {
        let p = player("p1", value: 2_000_000, change: nil)
        XCTAssertEqual(CalculatorMath.projectedValue(p, daysAhead: 5), 2_000_000)
    }

    // MARK: - 3. projectedValue negative trend and day clamp (BR1.2)

    func testProjectedValueNegativeTrendAndDayClamp() {
        let p = player("p1", value: 1_000_000, change: -40_000)
        XCTAssertEqual(CalculatorMath.projectedValue(p, daysAhead: 2), 920_000, "negative trend lowers it")
        XCTAssertEqual(CalculatorMath.projectedValue(p, daysAhead: -5), 1_000_000, "negative days clamp to 0")
    }

    // MARK: - 4. selectedTotal sums projected values of selected ids only (BR2.1)

    func testSelectedTotalSumsOnlySelected() {
        let players = [
            player("a", value: 1_000_000, change: 10_000),
            player("b", value: 2_000_000, change: 20_000),
            player("c", value: 3_000_000, change: 30_000)
        ]
        let selected: Set<String> = ["a", "c"]
        // day 2: a = 1_020_000, c = 3_060_000 → 4_080_000 (b excluded).
        XCTAssertEqual(
            CalculatorMath.selectedTotal(players: players, selectedIds: selected, daysAhead: 2),
            4_080_000
        )
    }

    func testSelectedTotalEmptySelectionIsZero() {
        let players = [player("a", value: 1_000_000, change: 10_000)]
        XCTAssertEqual(
            CalculatorMath.selectedTotal(players: players, selectedIds: [], daysAhead: 3),
            0
        )
    }

    // MARK: - 5. onSaleTotal sums value (not projected) (BR2.2)

    func testOnSaleTotalSumsValue() {
        let onSalePlayers = [onSale("x", value: 500_000), onSale("y", value: 1_500_000)]
        XCTAssertEqual(CalculatorMath.onSaleTotal(onSalePlayers), 2_000_000)
        XCTAssertEqual(CalculatorMath.onSaleTotal([]), 0)
    }

    // MARK: - 6. futureBalance with toggle ON includes onSaleTotal (BR3.1)

    func testFutureBalanceToggleOnIncludesOnSale() {
        let future = CalculatorMath.futureBalance(
            balance: 10_000_000,
            selectedTotal: 4_000_000,
            onSaleTotal: 2_000_000,
            includeOnSale: true,
            activeBidsTotal: 3_000_000
        )
        // 10M + 4M + 2M - 3M = 13M.
        XCTAssertEqual(future, 13_000_000)
    }

    // MARK: - 7. futureBalance with toggle OFF excludes onSaleTotal (BR3.1)

    func testFutureBalanceToggleOffExcludesOnSale() {
        let future = CalculatorMath.futureBalance(
            balance: 10_000_000,
            selectedTotal: 4_000_000,
            onSaleTotal: 2_000_000,
            includeOnSale: false,
            activeBidsTotal: 3_000_000
        )
        // 10M + 4M + 0 - 3M = 11M.
        XCTAssertEqual(future, 11_000_000)
    }

    // MARK: - 8. activeBidsTotal is ALWAYS subtracted (BR3.2 invariant)

    func testActiveBidsTotalAlwaysSubtracted() {
        let on = CalculatorMath.futureBalance(
            balance: 5_000_000, selectedTotal: 0, onSaleTotal: 0,
            includeOnSale: true, activeBidsTotal: 1_200_000
        )
        let off = CalculatorMath.futureBalance(
            balance: 5_000_000, selectedTotal: 0, onSaleTotal: 0,
            includeOnSale: false, activeBidsTotal: 1_200_000
        )
        XCTAssertEqual(on, 3_800_000, "bids subtracted with toggle ON")
        XCTAssertEqual(off, 3_800_000, "bids subtracted with toggle OFF")
    }

    // MARK: - 9. anti-double-count: an on-sale player does not count twice (BR4.1)

    /// Models the toggle-ON policy: the on-sale player is EXCLUDED from the
    /// selectable list (counts via onSaleTotal), so it cannot also be in
    /// selectedIds. The whole future balance counts its value exactly once.
    func testAntiDoubleCountOnSalePlayerCountedOnce() {
        // Roster WITHOUT the on-sale player (toggle ON excludes it).
        let selectable = [player("a", value: 1_000_000, change: 0)]
        let onSalePlayers = [onSale("onsale", value: 2_000_000)]
        let selectedIds: Set<String> = ["a"] // only the roster player is selected

        let selectedTotal = CalculatorMath.selectedTotal(
            players: selectable, selectedIds: selectedIds, daysAhead: 0
        )
        let onSaleTotal = CalculatorMath.onSaleTotal(onSalePlayers)
        let future = CalculatorMath.futureBalance(
            balance: 0, selectedTotal: selectedTotal, onSaleTotal: onSaleTotal,
            includeOnSale: true, activeBidsTotal: 0
        )
        // a (1M) + onsale (2M) once = 3M; the on-sale value is NOT doubled.
        XCTAssertEqual(selectedTotal, 1_000_000)
        XCTAssertEqual(onSaleTotal, 2_000_000)
        XCTAssertEqual(future, 3_000_000)
    }

    // MARK: - 10. profit never enters futureBalance (BR7.1 / R-03)

    /// Profit is presentation-only. A roster of players with large `profit`
    /// values contributes NOTHING to the money math beyond their `value`.
    func testProfitNeverAffectsMoneyMath() {
        let players = [player("a", value: 1_000_000, change: 0, profit: 9_999_999)]
        let selectedTotal = CalculatorMath.selectedTotal(
            players: players, selectedIds: ["a"], daysAhead: 0
        )
        XCTAssertEqual(selectedTotal, 1_000_000, "profit is not part of selectedTotal")
    }
}
