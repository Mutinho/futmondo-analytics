import XCTest
@testable import FutmondoKit

final class CalculatorSorterTests: XCTestCase {

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

    private func ids(_ players: [RosterPlayer]) -> [String] { players.map(\.playerId) }

    // MARK: - 1. value: descending

    func testSortByValueDescending() {
        let players = [
            player("a", value: 1_000_000),
            player("b", value: 3_000_000),
            player("c", value: 2_000_000)
        ]
        let sorted = CalculatorSorter.sorted(players, by: .value, daysAhead: 0)
        XCTAssertEqual(ids(sorted), ["b", "c", "a"])
    }

    // MARK: - 2. projectedValue uses daysAhead (BR1.1)

    func testSortByProjectedValueUsesDays() {
        // At day 0: a=1M, b=1.2M → b,a. At day 10: a=1M+10*50k=1.5M,
        // b=1.2M+10*0=1.2M → a,b (the trend flips the order).
        let players = [
            player("a", value: 1_000_000, change: 50_000),
            player("b", value: 1_200_000, change: 0)
        ]
        XCTAssertEqual(ids(CalculatorSorter.sorted(players, by: .projectedValue, daysAhead: 0)), ["b", "a"])
        XCTAssertEqual(ids(CalculatorSorter.sorted(players, by: .projectedValue, daysAhead: 10)), ["a", "b"])
    }

    // MARK: - 3. change: descending, nils last

    func testSortByChangeNilsLast() {
        let players = [
            player("a", value: 1, change: nil),
            player("b", value: 1, change: 100),
            player("c", value: 1, change: -50),
            player("d", value: 1, change: nil)
        ]
        let sorted = CalculatorSorter.sorted(players, by: .change, daysAhead: 0)
        // b(100), c(-50), then the two nils stably (a before d).
        XCTAssertEqual(ids(sorted), ["b", "c", "a", "d"])
    }

    // MARK: - 4. profit: descending, nils last (BR7.1)

    func testSortByProfitNilsLast() {
        let players = [
            player("a", value: 1, profit: nil),
            player("b", value: 1, profit: 500_000),
            player("c", value: 1, profit: 100_000)
        ]
        let sorted = CalculatorSorter.sorted(players, by: .profit, daysAhead: 0)
        XCTAssertEqual(ids(sorted), ["b", "c", "a"])
    }

    // MARK: - 5. stable tie-break preserves input order among equals

    func testStableTieBreak() {
        let players = [
            player("a", value: 1_000_000),
            player("b", value: 1_000_000),
            player("c", value: 1_000_000)
        ]
        let sorted = CalculatorSorter.sorted(players, by: .value, daysAhead: 0)
        XCTAssertEqual(ids(sorted), ["a", "b", "c"], "equal values keep input order")
    }

    // MARK: - 6. empty input returns empty

    func testSortEmpty() {
        XCTAssertTrue(CalculatorSorter.sorted([], by: .value, daysAhead: 0).isEmpty)
    }

    // MARK: - 7. default field is projectedValue

    func testDefaultFieldIsProjectedValue() {
        XCTAssertEqual(CalculatorSortField.defaultField, .projectedValue)
        XCTAssertEqual(CalculatorSortField.allCases.count, 4)
    }
}
