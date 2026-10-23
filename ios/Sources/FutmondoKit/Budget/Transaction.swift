import Foundation

/// One market operation of a team (FR6). Appears in the `purchases[]` or
/// `sales[]` arrays of a ``TeamDetailResponse``.
///
/// Snake_case wire keys from the FastAPI backend are mapped through
/// ``CodingKeys``. `from` carries the *procedencia* on a purchase and `to` the
/// *destino* on a sale; both are optional because only one is meaningful per
/// list and the backend may omit the other.
///
/// `Equatable` so it can ride inside the ``TeamDetailResponse`` payload of an
/// `Equatable` view state (`TeamDetailViewModel`); `Sendable` so it crosses the
/// `async` service boundary safely (Swift 6 strict concurrency).
public struct Transaction: Codable, Sendable, Equatable, Identifiable {
    public let playerId: String
    public let playerName: String
    public let price: Int
    public let date: String
    /// Procedencia (present on a purchase).
    public let from: String?
    /// Destino (present on a sale).
    public let to: String?

    /// `Identifiable` conformance. A player can appear in both lists, and the
    /// backend does not expose a per-operation id, so the identity composes the
    /// player id with the date to stay stable within one list.
    public var id: String { "\(playerId)#\(date)" }

    private enum CodingKeys: String, CodingKey {
        case playerId = "player_id"
        case playerName = "player_name"
        case price
        case date
        case from
        case to
    }

    public init(
        playerId: String,
        playerName: String,
        price: Int,
        date: String,
        from: String? = nil,
        to: String? = nil
    ) {
        self.playerId = playerId
        self.playerName = playerName
        self.price = price
        self.date = date
        self.from = from
        self.to = to
    }
}
