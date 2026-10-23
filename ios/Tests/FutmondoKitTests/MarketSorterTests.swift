import XCTest
@testable import FutmondoKit

final class MarketSorterTests: XCTestCase {
    /// Build a player with only the fields the sort tests exercise.
    private func player(
        id: String,
        value: Int = 0,
        change: Int? = nil,
        sofascoreRating: Double? = nil,
        starterPct: Int? = nil,
        suggestedBid: Int = 0,
        points: Int? = nil,
        average: Double? = nil
    ) -> MarketPlayer {
        MarketPlayer(
            playerId: id, slug: id, name: id, team: "T",
            value: value, marketPrice: 0, change: change,
            average: average, points: points, suggestedBid: suggestedBid,
            sofascoreRating: sofascoreRating, starterPct: starterPct
        )
    }

    private func ids(_ players: [MarketPlayer]) -> [String] { players.map(\.playerId) }

    // MARK: - 1. Default field is value, descending

    func testSortByValueDescending() {
        let input = [
            player(id: "a", value: 10),
            player(id: "b", value: 30),
            player(id: "c", value: 20),
        ]
        let sorted = MarketSorter.sorted(input, by: .value)
        XCTAssertEqual(ids(sorted), ["b", "c", "a"])
        XCTAssertEqual(MarketSortField.defaultField, .value)
    }

    // MARK: - 2. Nulls last on an Int? field (change)

    func testSortByChangeNullsLast() {
        let input = [
            player(id: "a", change: nil),
            player(id: "b", change: 5),
            player(id: "c", change: nil),
            player(id: "d", change: 10),
        ]
        let sorted = MarketSorter.sorted(input, by: .change)
        // Present values descending first, then nulls in stable input order.
        XCTAssertEqual(ids(sorted), ["d", "b", "a", "c"])
    }

    // MARK: - 3. Nulls last on a Double? field (sofascore_rating)

    func testSortBySofascoreRatingNullsLast() {
        let input = [
            player(id: "a", sofascoreRating: 7.1),
            player(id: "b", sofascoreRating: nil),
            player(id: "c", sofascoreRating: 8.9),
        ]
        let sorted = MarketSorter.sorted(input, by: .sofascoreRating)
        XCTAssertEqual(ids(sorted), ["c", "a", "b"])
    }

    // MARK: - 4. starter_pct descending

    func testSortByStarterPct() {
        let input = [
            player(id: "a", starterPct: 40),
            player(id: "b", starterPct: 90),
            player(id: "c", starterPct: 65),
        ]
        XCTAssertEqual(ids(MarketSorter.sorted(input, by: .starterPct)), ["b", "c", "a"])
    }

    // MARK: - 5. suggested_bid descending

    func testSortBySuggestedBid() {
        let input = [
            player(id: "a", suggestedBid: 1_000),
            player(id: "b", suggestedBid: 9_000),
            player(id: "c", suggestedBid: 5_000),
        ]
        XCTAssertEqual(ids(MarketSorter.sorted(input, by: .suggestedBid)), ["b", "c", "a"])
    }

    // MARK: - 6. points & average descending with nulls last

    func testSortByPointsAndAverage() {
        let byPoints = [
            player(id: "a", points: nil),
            player(id: "b", points: 100),
            player(id: "c", points: 50),
        ]
        XCTAssertEqual(ids(MarketSorter.sorted(byPoints, by: .points)), ["b", "c", "a"])

        let byAverage = [
            player(id: "x", average: 6.2),
            player(id: "y", average: nil),
            player(id: "z", average: 7.7),
        ]
        XCTAssertEqual(ids(MarketSorter.sorted(byAverage, by: .average)), ["z", "x", "y"])
    }

    // MARK: - 7. Stable tie-break keeps input order for equal keys

    func testSortIsStableForEqualKeys() {
        let input = [
            player(id: "a", value: 10),
            player(id: "b", value: 10),
            player(id: "c", value: 10),
        ]
        // All equal → original order preserved.
        XCTAssertEqual(ids(MarketSorter.sorted(input, by: .value)), ["a", "b", "c"])
    }

    // MARK: - 8. Empty and single-element inputs are safe

    func testSortEdgeCases() {
        XCTAssertTrue(MarketSorter.sorted([], by: .value).isEmpty)
        let one = [player(id: "only", value: 5)]
        XCTAssertEqual(ids(MarketSorter.sorted(one, by: .value)), ["only"])
    }
}
