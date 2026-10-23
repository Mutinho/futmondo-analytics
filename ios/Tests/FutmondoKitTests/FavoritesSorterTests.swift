import XCTest
@testable import FutmondoKit

final class FavoritesSorterTests: XCTestCase {

    private func player(
        _ id: String,
        value: Int = 1,
        change: Int? = nil,
        points: Int? = nil,
        sofascoreRating: Double? = nil,
        starterPct: Int? = nil
    ) -> FavoritePlayer {
        FavoritePlayer(
            playerId: id,
            name: id,
            slug: id,
            team: "T",
            value: value,
            change: change,
            points: points,
            sofascoreRating: sofascoreRating,
            starterPct: starterPct
        )
    }

    private func ids(_ players: [FavoritePlayer]) -> [String] { players.map(\.playerId) }

    // MARK: - 1. value: descending

    func testSortByValueDescending() {
        let players = [
            player("a", value: 1_000_000),
            player("b", value: 3_000_000),
            player("c", value: 2_000_000)
        ]
        XCTAssertEqual(ids(FavoritesSorter.sorted(players, by: .value)), ["b", "c", "a"])
    }

    // MARK: - 2. change: descending, nils last

    func testSortByChangeNilsLast() {
        let players = [
            player("a", change: nil),
            player("b", change: 100),
            player("c", change: -50),
            player("d", change: nil)
        ]
        // b(100), c(-50), then the two nils stably (a before d).
        XCTAssertEqual(ids(FavoritesSorter.sorted(players, by: .change)), ["b", "c", "a", "d"])
    }

    // MARK: - 3. sofascoreRating: descending, nils last (BR3.3 — NOT `rating`)

    func testSortBySofascoreRatingNilsLast() {
        let players = [
            player("a", sofascoreRating: nil),
            player("b", sofascoreRating: 7.8),
            player("c", sofascoreRating: 6.1)
        ]
        XCTAssertEqual(ids(FavoritesSorter.sorted(players, by: .sofascoreRating)), ["b", "c", "a"])
    }

    // MARK: - 4. starterPct: descending, nils last

    func testSortByStarterPctNilsLast() {
        let players = [
            player("a", starterPct: 40),
            player("b", starterPct: nil),
            player("c", starterPct: 95)
        ]
        XCTAssertEqual(ids(FavoritesSorter.sorted(players, by: .starterPct)), ["c", "a", "b"])
    }

    // MARK: - 5. points: descending, nils last

    func testSortByPointsNilsLast() {
        let players = [
            player("a", points: 10),
            player("b", points: 200),
            player("c", points: nil)
        ]
        XCTAssertEqual(ids(FavoritesSorter.sorted(players, by: .points)), ["b", "a", "c"])
    }

    // MARK: - 6. stable tie-break preserves input order among equals

    func testStableTieBreak() {
        let players = [
            player("a", value: 1_000_000),
            player("b", value: 1_000_000),
            player("c", value: 1_000_000)
        ]
        XCTAssertEqual(ids(FavoritesSorter.sorted(players, by: .value)), ["a", "b", "c"])
    }

    // MARK: - 7. empty input returns empty

    func testSortEmpty() {
        XCTAssertTrue(FavoritesSorter.sorted([], by: .value).isEmpty)
    }

    // MARK: - 8. default field is value and the enum has 5 cases

    func testDefaultFieldAndCases() {
        XCTAssertEqual(FavoritesSortField.defaultField, .value)
        XCTAssertEqual(FavoritesSortField.allCases.count, 5)
    }
}
