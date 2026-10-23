import Foundation

/// The `user_info` block of `GET /api/v1/market/today`, driving the economy
/// banner (FR3 / C2) and the Calculadora header (FR2.3 / entities.md
/// `EconomySnapshot`).
///
/// `balanceMinusBids` is a derived, non-wire property shown as "Balance" in the
/// banner (W2): `balance - active_bids_total`.
///
/// `activeBidsCount` (R-02): the number of open bids, consumed by the
/// Calculadora header ("Pujas activas (N)", BR6.2). It is an OPTIONAL-WITH-
/// DEFAULT wire field — `decodeIfPresent ?? 0`, and its init parameter is
/// defaulted AND placed LAST — so adding it breaks neither the existing
/// `market/today` decode nor the existing memberwise-init callers (the Mercado
/// screen never passes it).
public struct MarketUserInfo: Codable, Sendable, Equatable {
    public let balance: Int
    public let teamValue: Int
    public let maxBid: Int
    public let activeBidsTotal: Int
    public let availableForBids: Int
    public let activeBidsCount: Int

    /// Derived "Balance" figure: budget minus the amount already committed to
    /// open bids. Not a wire field (W2 / BR-UI-2 context).
    public var balanceMinusBids: Int { balance - activeBidsTotal }

    private enum CodingKeys: String, CodingKey {
        case balance
        case teamValue = "team_value"
        case maxBid = "max_bid"
        case activeBidsTotal = "active_bids_total"
        case availableForBids = "available_for_bids"
        case activeBidsCount = "active_bids_count"
    }

    public init(
        balance: Int,
        teamValue: Int,
        maxBid: Int,
        activeBidsTotal: Int,
        availableForBids: Int,
        activeBidsCount: Int = 0
    ) {
        self.balance = balance
        self.teamValue = teamValue
        self.maxBid = maxBid
        self.activeBidsTotal = activeBidsTotal
        self.availableForBids = availableForBids
        self.activeBidsCount = activeBidsCount
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.balance = try container.decode(Int.self, forKey: .balance)
        self.teamValue = try container.decode(Int.self, forKey: .teamValue)
        self.maxBid = try container.decode(Int.self, forKey: .maxBid)
        self.activeBidsTotal = try container.decode(Int.self, forKey: .activeBidsTotal)
        self.availableForBids = try container.decode(Int.self, forKey: .availableForBids)
        // R-02: absent/null `active_bids_count` decodes to 0 so the existing
        // `market/today` payloads (which never carried it) still decode.
        self.activeBidsCount = try container.decodeIfPresent(Int.self, forKey: .activeBidsCount) ?? 0
    }
}

/// Response of `GET /api/v1/market/today?championship_id=<id>` (FR2 / C1).
///
/// An empty `players` array decodes to an empty list (the view model maps it
/// to the empty state, W1). `userInfo` is required so the banner always has
/// data when the page loads.
public struct MarketTodayResponse: Codable, Sendable, Equatable {
    public let success: Bool
    public let players: [MarketPlayer]
    public let userInfo: MarketUserInfo

    private enum CodingKeys: String, CodingKey {
        case success
        case players
        case userInfo = "user_info"
    }

    public init(
        success: Bool,
        players: [MarketPlayer],
        userInfo: MarketUserInfo
    ) {
        self.success = success
        self.players = players
        self.userInfo = userInfo
    }
}
