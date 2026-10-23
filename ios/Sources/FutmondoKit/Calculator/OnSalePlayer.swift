import Foundation

/// A player the user already put on sale, from `GET /api/v1/roster/on-sale`
/// (FR1.1 / entities.md `OnSalePlayer`). Its `value` contributes to
/// `onSaleTotal` (BR2.2). It is a subset of ``RosterPlayer`` fields.
///
/// Per assumption A2, the backend returns at least `player_id`, `name`,
/// `slug`, `team`, and `value`; `team` is tolerated as optional so a sparse row
/// still decodes.
public struct OnSalePlayer: Codable, Sendable, Identifiable, Equatable {
    public let playerId: String
    public let name: String
    public let slug: String
    public let team: String?
    public let value: Int

    /// `Identifiable` conformance: the player id is the stable identity.
    public var id: String { playerId }

    private enum CodingKeys: String, CodingKey {
        case playerId = "player_id"
        case name
        case slug
        case team
        case value
    }

    public init(
        playerId: String,
        name: String,
        slug: String,
        team: String? = nil,
        value: Int
    ) {
        self.playerId = playerId
        self.name = name
        self.slug = slug
        self.team = team
        self.value = value
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.playerId = try container.decode(String.self, forKey: .playerId)
        self.name = try container.decode(String.self, forKey: .name)
        self.slug = try container.decode(String.self, forKey: .slug)
        self.team = try container.decodeIfPresent(String.self, forKey: .team)
        self.value = try container.decode(Int.self, forKey: .value)
    }
}

/// Response of `GET /api/v1/roster/on-sale?championship_id=<id>` (FR1.1 / C1).
///
/// Tolerant of the same root-array vs `players`-wrapped shapes as
/// ``RosterResponse``.
public struct OnSaleResponse: Codable, Sendable, Equatable {
    public let players: [OnSalePlayer]

    public init(players: [OnSalePlayer]) {
        self.players = players
    }

    private enum CodingKeys: String, CodingKey {
        case players
    }

    public init(from decoder: Decoder) throws {
        if let single = try? decoder.singleValueContainer(),
           let array = try? single.decode([OnSalePlayer].self) {
            self.players = array
            return
        }
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.players = try container.decodeIfPresent([OnSalePlayer].self, forKey: .players) ?? []
    }
}
