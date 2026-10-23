import Foundation

/// One favourite free player returned by `GET /api/v1/favorites/my` (FR1.1 /
/// FR3.2 / entities.md `FavoritePlayer`). It is the card (row) of the Favoritos
/// screen.
///
/// Snake_case wire keys from the FastAPI backend are mapped through
/// ``CodingKeys``. It is a DEDICATED model (not a reuse of ``RosterPlayer``):
/// it adds `homeAverage`/`awayAverage`/`rating` and drops `buyPrice`/`profit`.
/// Optionality follows the backend contract: identity, `team`, and `value` are
/// required; every analytics field (`change`, `points`, `average`,
/// `homeAverage`, `awayAverage`, `matches`, `rating`, `sofascoreRating`,
/// `sofascoreUrl`, `starterPct`, `status`) decodes to `nil` when the server
/// omits it or sends JSON `null`, which ``FavoritesSorter`` sends to the end of
/// a descending sort.
///
/// Two ratings (BR3.3): `sofascoreRating` drives the card badge and the sort,
/// while `rating` is an informative backend field that is decoded (tolerantly,
/// via `decodeIfPresent`) but NEVER shown on the card.
public struct FavoritePlayer: Codable, Sendable, Identifiable, Equatable {
    public let playerId: String
    public let name: String
    public let slug: String
    public let position: String?
    public let position2: String?
    public let team: String
    public let teamLogo: String?
    public let value: Int
    public let change: Int?
    public let points: Int?
    public let average: Double?
    public let homeAverage: Double?
    public let awayAverage: Double?
    public let matches: Int?
    /// Informative backend field; NOT shown on the card (BR3.3 / R-02). The
    /// web types it as a non-optional number, but it is decoded as optional
    /// here by TOLERANCE (`decodeIfPresent`) so the page still decodes if the
    /// backend omits it.
    public let rating: Double?
    /// The card badge and the sort criterion (BR3.3 / R-02).
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
        case change
        case points
        case average
        case homeAverage = "home_average"
        case awayAverage = "away_average"
        case matches
        case rating
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
        change: Int? = nil,
        points: Int? = nil,
        average: Double? = nil,
        homeAverage: Double? = nil,
        awayAverage: Double? = nil,
        matches: Int? = nil,
        rating: Double? = nil,
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
        self.change = change
        self.points = points
        self.average = average
        self.homeAverage = homeAverage
        self.awayAverage = awayAverage
        self.matches = matches
        self.rating = rating
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
        self.change = try container.decodeIfPresent(Int.self, forKey: .change)
        self.points = try container.decodeIfPresent(Int.self, forKey: .points)
        self.average = try container.decodeIfPresent(Double.self, forKey: .average)
        self.homeAverage = try container.decodeIfPresent(Double.self, forKey: .homeAverage)
        self.awayAverage = try container.decodeIfPresent(Double.self, forKey: .awayAverage)
        self.matches = try container.decodeIfPresent(Int.self, forKey: .matches)
        self.rating = try container.decodeIfPresent(Double.self, forKey: .rating)
        self.sofascoreRating = try container.decodeIfPresent(Double.self, forKey: .sofascoreRating)
        self.sofascoreUrl = try container.decodeIfPresent(String.self, forKey: .sofascoreUrl)
        self.starterPct = try container.decodeIfPresent(Int.self, forKey: .starterPct)
        self.status = try container.decodeIfPresent(String.self, forKey: .status)
    }
}

/// Response of `GET /api/v1/favorites/my?championship_id=<id>` (FR1.1 / C1).
///
/// The backend may return the favourites at the root as an array, or wrapped
/// under a `players` (or legacy `favorites`) key. ``FavoritesService`` decodes
/// this tolerant wrapper so either shape yields the player list
/// (native-ios-ui-patterns.md "wrapped vs root").
public struct FavoritesResponse: Codable, Sendable, Equatable {
    public let players: [FavoritePlayer]

    public init(players: [FavoritePlayer]) {
        self.players = players
    }

    /// Keys the tolerant wrapped shape may use. `players` is the canonical key
    /// and the only one written back when encoding; `favorites` is a legacy
    /// alias accepted on decode only.
    private enum CodingKeys: String, CodingKey {
        case players
        case favorites
    }

    public init(from decoder: Decoder) throws {
        // Preferred shape: a bare array of players at the root.
        if let single = try? decoder.singleValueContainer(),
           let array = try? single.decode([FavoritePlayer].self) {
            self.players = array
            return
        }
        // Wrapped shape: `{ "players": [...] }`, `{ "favorites": [...] }`, or
        // absent → empty.
        let container = try decoder.container(keyedBy: CodingKeys.self)
        if let players = try container.decodeIfPresent([FavoritePlayer].self, forKey: .players) {
            self.players = players
        } else {
            self.players = try container.decodeIfPresent([FavoritePlayer].self, forKey: .favorites) ?? []
        }
    }

    /// Encode under the canonical `players` key (the legacy `favorites` alias
    /// is decode-only). Written explicitly so the synthesized encoder does not
    /// have to reconcile the extra decode-only key.
    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(players, forKey: .players)
    }
}
