import Foundation

/// A championship the user can select. The core fields are always present on
/// the primary endpoint; the extras are optional so the fallback/legacy
/// endpoint subset decodes without failing (SR4).
public struct Championship: Codable, Sendable, Identifiable {
    public let championshipId: String
    public let name: String
    public let initialBudget: Int
    public let hasClauses: Bool
    public let excludedTeams: [String]

    // Optional extras (legacy-tolerant): absent on the subset endpoint.
    public let moneyPerPoint: Int?
    public let moneyPerRanking: Int?
    public let dreamTeamBonus: Int?
    public let mvpBonus: Int?
    public let rankingMode: String?
    public let usersToRank: Int?

    /// `Identifiable` conformance: the championship id is the stable identity.
    public var id: String { championshipId }

    private enum CodingKeys: String, CodingKey {
        case championshipId = "championship_id"
        case name
        case initialBudget = "initial_budget"
        case hasClauses = "has_clauses"
        case excludedTeams = "excluded_teams"
        case moneyPerPoint = "money_per_point"
        case moneyPerRanking = "money_per_ranking"
        case dreamTeamBonus = "dream_team_bonus"
        case mvpBonus = "mvp_bonus"
        case rankingMode = "ranking_mode"
        case usersToRank = "users_to_rank"
    }

    public init(
        championshipId: String,
        name: String,
        initialBudget: Int,
        hasClauses: Bool,
        excludedTeams: [String],
        moneyPerPoint: Int? = nil,
        moneyPerRanking: Int? = nil,
        dreamTeamBonus: Int? = nil,
        mvpBonus: Int? = nil,
        rankingMode: String? = nil,
        usersToRank: Int? = nil
    ) {
        self.championshipId = championshipId
        self.name = name
        self.initialBudget = initialBudget
        self.hasClauses = hasClauses
        self.excludedTeams = excludedTeams
        self.moneyPerPoint = moneyPerPoint
        self.moneyPerRanking = moneyPerRanking
        self.dreamTeamBonus = dreamTeamBonus
        self.mvpBonus = mvpBonus
        self.rankingMode = rankingMode
        self.usersToRank = usersToRank
    }
}
