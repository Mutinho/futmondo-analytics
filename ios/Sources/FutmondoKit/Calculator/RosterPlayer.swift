import Foundation

/// One row of the user's roster from `GET /api/v1/roster/my` (FR1.1 / FR5 /
/// entities.md `RosterPlayer`). It is the selectable row of the Calculadora.
///
/// Snake_case wire keys from the FastAPI backend are mapped through
/// ``CodingKeys``. It does NOT reuse ``MarketPlayer`` because it adds
/// `buyPrice`/`profit`/`status`. Optionality follows the backend contract:
/// identity and `value` are required; the analytics fields (`change`,
/// `profit`, `sofascoreRating`, `starterPct`, `points`, `average`, `matches`)
/// decode to `nil` when the server omits them or sends JSON `null`, which
/// ``CalculatorSorter`` sends to the end of a descending sort.
///
/// `change` is the per-day trend (€/day) used by projection (BR1.1); `profit`
/// is the presentation-only plusvalía (BR7.1) — it NEVER enters the money
/// invariants (FR7).
public struct RosterPlayer: Codable, Sendable, Identifiable, Equatable {
    public let playerId: String
    public let name: String
    public let slug: String
    public let position: String?
    public let position2: String?
    public let team: String
    public let teamLogo: String?
    public let value: Int
    public let buyPrice: Int?
    public let profit: Int?
    public let change: Int?
    public let points: Int?
    public let average: Double?
    public let matches: Int?
    public let sofascoreRating: Double?
    public let sofascoreUrl: String?
    public let starterPct: Int?
    public let status: String?

    /// `Identifiable` conformance: the player id is the stable identity.
    public var id: String { playerId }

    private enum CodingKeys: String, CodingKey {
        case playerId = "player_id"
        case name
        case slug
        case position
        case position2
        case team
        case teamLogo = "team_logo"
        case value
        case buyPrice = "buy_price"
        case profit
        case change
        case points
        case average
        case matches
        case sofascoreRating = "sofascore_rating"
        case sofascoreUrl = "sofascore_url"
        case starterPct = "starter_pct"
        case status
    }

    public init(
        playerId: String,
        name: String,
        slug: String,
        position: String? = nil,
        position2: String? = nil,
        team: String,
        teamLogo: String? = nil,
        value: Int,
        buyPrice: Int? = nil,
        profit: Int? = nil,
        change: Int? = nil,
        points: Int? = nil,
        average: Double? = nil,
        matches: Int? = nil,
        sofascoreRating: Double? = nil,
        sofascoreUrl: String? = nil,
        starterPct: Int? = nil,
        status: String? = nil
    ) {
        self.playerId = playerId
        self.name = name
        self.slug = slug
        self.position = position
        self.position2 = position2
        self.team = team
        self.teamLogo = teamLogo
        self.value = value
        self.buyPrice = buyPrice
        self.profit = profit
        self.change = change
        self.points = points
        self.average = average
        self.matches = matches
        self.sofascoreRating = sofascoreRating
        self.sofascoreUrl = sofascoreUrl
        self.starterPct = starterPct
        self.status = status
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.playerId = try container.decode(String.self, forKey: .playerId)
        self.name = try container.decode(String.self, forKey: .name)
        self.slug = try container.decode(String.self, forKey: .slug)
        self.position = try container.decodeIfPresent(String.self, forKey: .position)
        self.position2 = try container.decodeIfPresent(String.self, forKey: .position2)
        self.team = try container.decode(String.self, forKey: .team)
        self.teamLogo = try container.decodeIfPresent(String.self, forKey: .teamLogo)
        self.value = try container.decode(Int.self, forKey: .value)
        self.buyPrice = try container.decodeIfPresent(Int.self, forKey: .buyPrice)
        self.profit = try container.decodeIfPresent(Int.self, forKey: .profit)
        self.change = try container.decodeIfPresent(Int.self, forKey: .change)
        self.points = try container.decodeIfPresent(Int.self, forKey: .points)
        self.average = try container.decodeIfPresent(Double.self, forKey: .average)
        self.matches = try container.decodeIfPresent(Int.self, forKey: .matches)
        self.sofascoreRating = try container.decodeIfPresent(Double.self, forKey: .sofascoreRating)
        self.sofascoreUrl = try container.decodeIfPresent(String.self, forKey: .sofascoreUrl)
        self.starterPct = try container.decodeIfPresent(Int.self, forKey: .starterPct)
        self.status = try container.decodeIfPresent(String.self, forKey: .status)
    }
}

/// Response of `GET /api/v1/roster/my?championship_id=<id>` (FR1.1 / C1).
///
/// The backend may return the roster at the root as an array, or wrapped under
/// a `players` key. ``RosterService`` decodes this tolerant wrapper so either
/// shape yields the player list (native-ios-ui-patterns.md "wrapped vs root").
public struct RosterResponse: Codable, Sendable, Equatable {
    public let players: [RosterPlayer]

    public init(players: [RosterPlayer]) {
        self.players = players
    }

    private enum CodingKeys: String, CodingKey {
        case players
    }

    public init(from decoder: Decoder) throws {
        // Preferred shape: a bare array of players at the root.
        if let single = try? decoder.singleValueContainer(),
           let array = try? single.decode([RosterPlayer].self) {
            self.players = array
            return
        }
        // Wrapped shape: `{ "players": [...] }` (or absent → empty).
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.players = try container.decodeIfPresent([RosterPlayer].self, forKey: .players) ?? []
    }
}
