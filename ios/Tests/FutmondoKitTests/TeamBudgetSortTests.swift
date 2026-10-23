import XCTest
@testable import FutmondoKit

final class TeamBudgetSortTests: XCTestCase {

    /// Builds a `TeamBudget` with only the fields a test cares about; the rest
    /// default to 0.
    private func team(
        id: String,
        balance: Int = 0,
        performance: Int = 0,
        maxBid: Int = 0,
        teamValue: Int = 0,
        totalSpent: Int = 0,
        totalIncome: Int = 0
    ) -> TeamBudget {
        TeamBudget(
            teamId: id,
            teamName: "Team \(id)",
            balance: balance,
            initialBudget: 0,
            totalSpent: totalSpent,
            totalIncome: totalIncome,
            purchasesCount: 0,
            salesCount: 0,
            teamValue: teamValue,
            performance: performance,
            maxBid: maxBid,
            prizes: 0
        )
    }

    // MARK: - 1. Descending by balance (happy path)

    func testSortsDescendingByBalance() {
        let teams = [team(id: "a", balance: 10), team(id: "b", balance: 30), team(id: "c", balance: 20)]
        let sorted = TeamBudgetSort.sorted(teams, by: .balance)
        XCTAssertEqual(sorted.map(\.teamId), ["b", "c", "a"])
    }

    // MARK: - 2. Descending by each key

    func testSortsDescendingByEachKey() {
        let keyed: [(SortKey, TeamBudget, TeamBudget)] = [
            (.performance, team(id: "lo", performance: 1), team(id: "hi", performance: 9)),
            (.maxBid, team(id: "lo", maxBid: 1), team(id: "hi", maxBid: 9)),
            (.teamValue, team(id: "lo", teamValue: 1), team(id: "hi", teamValue: 9)),
            (.totalSpent, team(id: "lo", totalSpent: 1), team(id: "hi", totalSpent: 9)),
            (.totalIncome, team(id: "lo", totalIncome: 1), team(id: "hi", totalIncome: 9))
        ]
        for (key, lo, hi) in keyed {
            let sorted = TeamBudgetSort.sorted([lo, hi], by: key)
            XCTAssertEqual(sorted.map(\.teamId), ["hi", "lo"], "key \(key)")
        }
    }

    // MARK: - 3. Stability on ties

    func testTiesKeepRelativeInputOrder() {
        // All equal on `balance`: output order must equal input order.
        let teams = [team(id: "a"), team(id: "b"), team(id: "c"), team(id: "d")]
        let sorted = TeamBudgetSort.sorted(teams, by: .balance)
        XCTAssertEqual(sorted.map(\.teamId), ["a", "b", "c", "d"])
    }

    // MARK: - 4. Partial ties preserve order within the tie group

    func testPartialTiesPreserveOrder() {
        let teams = [
            team(id: "a", balance: 5),
            team(id: "b", balance: 5),
            team(id: "c", balance: 9),
            team(id: "d", balance: 5)
        ]
        let sorted = TeamBudgetSort.sorted(teams, by: .balance)
        // c first (9), then the 5-group in original order a, b, d.
        XCTAssertEqual(sorted.map(\.teamId), ["c", "a", "b", "d"])
    }

    // MARK: - 5. Input is not mutated

    func testInputIsNotMutated() {
        let teams = [team(id: "a", balance: 1), team(id: "b", balance: 2)]
        let before = teams.map(\.teamId)
        _ = TeamBudgetSort.sorted(teams, by: .balance)
        XCTAssertEqual(teams.map(\.teamId), before, "sorted() must not mutate its input")
    }

    // MARK: - 6. Empty input

    func testEmptyInputReturnsEmpty() {
        XCTAssertTrue(TeamBudgetSort.sorted([], by: .balance).isEmpty)
    }
}
