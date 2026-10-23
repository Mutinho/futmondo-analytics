import Foundation

/// Player statistics from `GET /api/v1/sofascore/player/{player_name}` (FR8 /
/// C8). Mirrors the Angular `SofascoreStats` (~19 fields). Only `playerName`
/// and `rating` are treated as required; everything else is optional so a
/// sparse row still decodes and renders what it has (W7).
public struct SofascoreDetail: Codable, Sendable, Equatable {
    public let playerName: String
    public let rating: Double?
    public let goals: Int?
    public let assists: Int?
    public let appearances: Int?
    public let matchesStarted: Int?
    public let starterPct: Int?
    public let minutesPlayed: Int?
    public let yellowCards: Int?
    public let redCards: Int?
    public let tournament: String?
    public let season: String?
    public let successfulDribbles: Double?
    public let accuratePassesPct: Double?
    public let shotsOnTarget: Double?
    public let tackles: Double?
    public let interceptions: Double?
    public let cleanSheets: Int?
    public let saves: Int?
    public let syncedAt: String?

    private enum CodingKeys: String, CodingKey {
        case playerName = "player_name"
        case rating
        case goals
        case assists
        case appearances
        case matchesStarted = "matches_started"
        case starterPct = "starter_pct"
        case minutesPlayed = "minutes_played"
        case yellowCards = "yellow_cards"
        case redCards = "red_cards"
        case tournament
        case season
        case successfulDribbles = "successful_dribbles"
        case accuratePassesPct = "accurate_passes_pct"
        case shotsOnTarget = "shots_on_target"
        case tackles
        case interceptions
        case cleanSheets = "clean_sheets"
        case saves
        case syncedAt = "synced_at"
    }

    public init(
        playerName: String,
        rating: Double? = nil,
        goals: Int? = nil,
        assists: Int? = nil,
        appearances: Int? = nil,
        matchesStarted: Int? = nil,
        starterPct: Int? = nil,
        minutesPlayed: Int? = nil,
        yellowCards: Int? = nil,
        redCards: Int? = nil,
        tournament: String? = nil,
        season: String? = nil,
        successfulDribbles: Double? = nil,
        accuratePassesPct: Double? = nil,
        shotsOnTarget: Double? = nil,
        tackles: Double? = nil,
        interceptions: Double? = nil,
        cleanSheets: Int? = nil,
        saves: Int? = nil,
        syncedAt: String? = nil
    ) {
        self.playerName = playerName
        self.rating = rating
        self.goals = goals
        self.assists = assists
        self.appearances = appearances
        self.matchesStarted = matchesStarted
        self.starterPct = starterPct
        self.minutesPlayed = minutesPlayed
        self.yellowCards = yellowCards
        self.redCards = redCards
        self.tournament = tournament
        self.season = season
        self.successfulDribbles = successfulDribbles
        self.accuratePassesPct = accuratePassesPct
        self.shotsOnTarget = shotsOnTarget
        self.tackles = tackles
        self.interceptions = interceptions
        self.cleanSheets = cleanSheets
        self.saves = saves
        self.syncedAt = syncedAt
    }
}

/// Typed outcome of a Sofascore-detail fetch (W7 / FR8.2). Isolated from the
/// market list state: a failure here never degrades the list or bidding.
///
/// - `.loaded`: 2xx with stats.
/// - `.empty`: HTTP 404 — "sin datos" inside the sheet (not an error).
/// - `.failed`: any other failure (transport, 5xx, decode, other 4xx).
public enum SofascoreDetailOutcome: Sendable, Equatable {
    case loaded(SofascoreDetail)
    case empty
    case failed
}

/// Wire envelope of `GET /api/v1/sofascore/player/{name}`: the backend nests
/// the stats under a `player` key (`{ "success": true, "player": { … } }`),
/// NOT at the root. Decoding straight into `SofascoreDetail` therefore failed —
/// this wrapper unwraps it. `player` is optional so a `{success:false}` body
/// degrades to `.empty`/`.failed` rather than a decode crash.
public struct SofascoreDetailResponse: Codable, Sendable, Equatable {
    public let success: Bool
    public let player: SofascoreDetail?

    public init(success: Bool, player: SofascoreDetail?) {
        self.success = success
        self.player = player
    }
}
