import Foundation

/// Response of `GET /api/v1/user/championships` (and the `GET
/// /api/v1/championships` fallback, which returns a subset of each
/// championship).
public struct ChampionshipsResponse: Codable, Sendable {
    public let success: Bool
    public let championships: [Championship]

    public init(success: Bool, championships: [Championship]) {
        self.success = success
        self.championships = championships
    }
}
