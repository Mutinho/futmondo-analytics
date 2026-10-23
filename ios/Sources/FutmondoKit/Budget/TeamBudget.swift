import Foundation

/// One row of `teams[]` in the balances response (12 wire properties).
///
/// Snake_case wire keys from the FastAPI backend are mapped through
/// ``CodingKeys``. `ops` is a derived, non-wire property
/// (`purchasesCount + salesCount`).
public struct TeamBudget: Codable, Sendable, Identifiable, Equatable {
    public let teamId: String
    public let teamName: String
    public let balance: Int
    public let initialBudget: Int
    public let totalSpent: Int
    public let totalIncome: Int
    public let purchasesCount: Int
    public let salesCount: Int
    public let teamValue: Int
    public let performance: Int
    public let maxBid: Int
    public let prizes: Int

    /// `Identifiable` conformance: the team id is the stable identity.
    public var id: String { teamId }

    /// Derived total number of market operations. Not a wire field.
    public var ops: Int { purchasesCount + salesCount }

    private enum CodingKeys: String, CodingKey {
        case teamId = "team_id"
        case teamName = "team_name"
        case balance
        case initialBudget = "initial_budget"
        case totalSpent = "total_spent"
        case totalIncome = "total_income"
        case purchasesCount = "purchases_count"
        case salesCount = "sales_count"
        case teamValue = "team_value"
        case performance
        case maxBid = "max_bid"
        case prizes
    }

    public init(
        teamId: String,
        teamName: String,
        balance: Int,
        initialBudget: Int,
        totalSpent: Int,
        totalIncome: Int,
        purchasesCount: Int,
        salesCount: Int,
        teamValue: Int,
        performance: Int,
        maxBid: Int,
        prizes: Int
    ) {
        self.teamId = teamId
        self.teamName = teamName
        self.balance = balance
        self.initialBudget = initialBudget
        self.totalSpent = totalSpent
        self.totalIncome = totalIncome
        self.purchasesCount = purchasesCount
        self.salesCount = salesCount
        self.teamValue = teamValue
        self.performance = performance
        self.maxBid = maxBid
        self.prizes = prizes
    }
}
