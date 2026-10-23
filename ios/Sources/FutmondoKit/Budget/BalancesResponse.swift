import Foundation

/// Response of `GET /api/v1/analytics/balances?championship_id=<id>`.
///
/// Snake_case wire keys mapped through ``CodingKeys``. An empty `teams` array
/// decodes to an empty list (the view model translates it to an empty state).
public struct BalancesResponse: Codable, Sendable {
    public let success: Bool
    public let championshipId: String
    public let initialBudget: Int
    public let teams: [TeamBudget]

    private enum CodingKeys: String, CodingKey {
        case success
        case championshipId = "championship_id"
        case initialBudget = "initial_budget"
        case teams
    }

    public init(
        success: Bool,
        championshipId: String,
        initialBudget: Int,
        teams: [TeamBudget]
    ) {
        self.success = success
        self.championshipId = championshipId
        self.initialBudget = initialBudget
        self.teams = teams
    }
}
