import Foundation

/// Response of `GET /api/v1/analytics/balances/{team_id}?championship_id=<id>`
/// (FR6 — team detail).
///
/// Snake_case wire keys mapped through ``CodingKeys``. Empty `purchases` /
/// `sales` arrays decode to empty lists (the view model translates each to a
/// per-section empty state).
///
/// `Equatable` so it can be the payload of an `Equatable` view state
/// (`TeamDetailViewModel.State.loaded`); `Sendable` so it crosses the `async`
/// service boundary safely (Swift 6 strict concurrency). ``Transaction`` is
/// likewise `Equatable` + `Sendable`, so the synthesis holds.
public struct TeamDetailResponse: Codable, Sendable, Equatable {
    public let success: Bool
    public let teamId: String
    public let teamName: String
    public let balance: Int
    public let initialBudget: Int
    public let totalSpent: Int
    public let totalIncome: Int
    public let purchases: [Transaction]
    public let sales: [Transaction]

    private enum CodingKeys: String, CodingKey {
        case success
        case teamId = "team_id"
        case teamName = "team_name"
        case balance
        case initialBudget = "initial_budget"
        case totalSpent = "total_spent"
        case totalIncome = "total_income"
        case purchases
        case sales
    }

    public init(
        success: Bool,
        teamId: String,
        teamName: String,
        balance: Int,
        initialBudget: Int,
        totalSpent: Int,
        totalIncome: Int,
        purchases: [Transaction],
        sales: [Transaction]
    ) {
        self.success = success
        self.teamId = teamId
        self.teamName = teamName
        self.balance = balance
        self.initialBudget = initialBudget
        self.totalSpent = totalSpent
        self.totalIncome = totalIncome
        self.purchases = purchases
        self.sales = sales
    }
}
