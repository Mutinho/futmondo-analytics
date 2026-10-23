import Foundation

/// One row of `players[]` in `GET /api/v1/market/today` (FR2 / C1).
///
/// Snake_case wire keys from the FastAPI backend are mapped through
/// ``CodingKeys``. The frontend consumes the subset the Angular `MarketPlayer`
/// interface declares; the backend may emit extra fields (`photo`,
/// `sofascore_id`, ...) that are simply ignored by the decoder.
///
/// Optionality follows the backend contract: identity and pricing fields are
/// required; the nullable analytics (`change`, `sofascore_rating`,
/// `starter_pct`, `average`, `points`) decode to `nil` when the server omits
/// them or sends JSON `null`, which `MarketSorter` sends to the end of a
/// descending sort.
public struct MarketPlayer: Codable, Sendable, Identifiable, Equatable {
    public let playerId: String
    public let slug: String
    public let name: String
    public let team: String
    public let teamLogo: String?
    public let position: String?
    public let position2: String?
    public let value: Int
    public let marketPrice: Int
    public let change: Int?
    public let currentBid: Int?
    public let currentBidId: String?
    public let average: Double?
    public let points: Int?
    public let matches: Int?
    public let suggestedBid: Int
    public let sofascoreRating: Double?
    public let sofascoreUrl: String?
    public let starterPct: Int?
    public let isFavorite: Bool

    /// `Identifiable` conformance: the player id is the stable identity.
    public var id: String { playerId }

    /// Whether the player currently has an active bid placed by the user
    /// (drives the "Pujar" vs. "Puja activa"/"Cancelar" affordance, W4/W5).
    ///
    /// Mirrors the Angular source of truth `@if (p.current_bid)`: the backend
    /// emits `current_bid: 0` (NOT null) when there is no active bid, and `0`
    /// is falsy in the web view. So an active bid requires a POSITIVE amount
    /// (`> 0`), not merely a non-nil value, plus a non-empty bid id to cancel.
    public var hasActiveBid: Bool {
        guard let currentBid, currentBid > 0 else { return false }
        guard let currentBidId, !currentBidId.isEmpty else { return false }
        return true
    }

    /// The active bid amount when `hasActiveBid` (always `> 0`), else `nil`.
    public var activeBidAmount: Int? { hasActiveBid ? currentBid : nil }

    private enum CodingKeys: String, CodingKey {
        case playerId = "player_id"
        case slug
        case name
        case team
        case teamLogo = "team_logo"
        case position
        case position2
        case value
        case marketPrice = "market_price"
        case change
        case currentBid = "current_bid"
        case currentBidId = "current_bid_id"
        case average
        case points
        case matches
        case suggestedBid = "suggested_bid"
        case sofascoreRating = "sofascore_rating"
        case sofascoreUrl = "sofascore_url"
        case starterPct = "starter_pct"
        case isFavorite = "is_favorite"
    }

    public init(
        playerId: String,
        slug: String,
        name: String,
        team: String,
        teamLogo: String? = nil,
        position: String? = nil,
        position2: String? = nil,
        value: Int,
        marketPrice: Int,
        change: Int? = nil,
        currentBid: Int? = nil,
        currentBidId: String? = nil,
        average: Double? = nil,
        points: Int? = nil,
        matches: Int? = nil,
        suggestedBid: Int,
        sofascoreRating: Double? = nil,
        sofascoreUrl: String? = nil,
        starterPct: Int? = nil,
        isFavorite: Bool = false
    ) {
        self.playerId = playerId
        self.slug = slug
        self.name = name
        self.team = team
        self.teamLogo = teamLogo
        self.position = position
        self.position2 = position2
        self.value = value
        self.marketPrice = marketPrice
        self.change = change
        self.currentBid = currentBid
        self.currentBidId = currentBidId
        self.average = average
        self.points = points
        self.matches = matches
        self.suggestedBid = suggestedBid
        self.sofascoreRating = sofascoreRating
        self.sofascoreUrl = sofascoreUrl
        self.starterPct = starterPct
        self.isFavorite = isFavorite
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.playerId = try container.decode(String.self, forKey: .playerId)
        self.slug = try container.decode(String.self, forKey: .slug)
        self.name = try container.decode(String.self, forKey: .name)
        self.team = try container.decode(String.self, forKey: .team)
        self.teamLogo = try container.decodeIfPresent(String.self, forKey: .teamLogo)
        self.position = try container.decodeIfPresent(String.self, forKey: .position)
        self.position2 = try container.decodeIfPresent(String.self, forKey: .position2)
        self.value = try container.decode(Int.self, forKey: .value)
        self.marketPrice = try container.decode(Int.self, forKey: .marketPrice)
        self.change = try container.decodeIfPresent(Int.self, forKey: .change)
        self.currentBid = try container.decodeIfPresent(Int.self, forKey: .currentBid)
        self.currentBidId = try container.decodeIfPresent(String.self, forKey: .currentBidId)
        self.average = try container.decodeIfPresent(Double.self, forKey: .average)
        self.points = try container.decodeIfPresent(Int.self, forKey: .points)
        self.matches = try container.decodeIfPresent(Int.self, forKey: .matches)
        self.suggestedBid = try container.decode(Int.self, forKey: .suggestedBid)
        self.sofascoreRating = try container.decodeIfPresent(Double.self, forKey: .sofascoreRating)
        self.sofascoreUrl = try container.decodeIfPresent(String.self, forKey: .sofascoreUrl)
        self.starterPct = try container.decodeIfPresent(Int.self, forKey: .starterPct)
        // The backend always emits `is_favorite`, but be tolerant: a missing
        // flag defaults to false rather than failing the whole page decode.
        self.isFavorite = try container.decodeIfPresent(Bool.self, forKey: .isFavorite) ?? false
    }
}
