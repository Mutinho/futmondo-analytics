import Foundation

/// Decoded body of a 2xx `POST /api/v1/roster/sell` response (FR8.3 / BR8.2).
///
/// The backend returns `{ "success", "total", "sold", "results" }`. `total` is
/// how many players the request tried to sell and `sold` how many actually
/// sold; `results` is an opaque per-player array the UI does not need, so it is
/// ignored by the decoder. Both counts are optional-with-default so a terse
/// `{ "success": true }` still decodes.
public struct SellResponse: Codable, Sendable, Equatable {
    public let success: Bool
    public let total: Int
    public let sold: Int

    public init(success: Bool, total: Int = 0, sold: Int = 0) {
        self.success = success
        self.total = total
        self.sold = sold
    }

    private enum CodingKeys: String, CodingKey {
        case success
        case total
        case sold
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.success = try container.decodeIfPresent(Bool.self, forKey: .success) ?? false
        self.total = try container.decodeIfPresent(Int.self, forKey: .total) ?? 0
        self.sold = try container.decodeIfPresent(Int.self, forKey: .sold) ?? 0
    }
}

/// The DEDICATED outcome of putting players on sale (FR8 / BR8.2 / R-01).
///
/// It does NOT reuse ``MarketWriteOutcome`` because it must transport
/// `sold`/`total` from `/roster/sell` so the UI can distinguish a full sale
/// (which removes players and reloads on-sale) from a partial one (which only
/// informs and keeps the list/selection). A sum type (enum):
///
/// - `.total(sold)`: `sold == total` — the full request sold. Remove the sold
///   players, clear the selection, reload on-sale, invalidate caches.
/// - `.partial(sold, total)`: `0 < sold < total` — inform `sold/total`; do NOT
///   remove, do NOT reload.
/// - `.none(total)`: `sold == 0` — inform the failure; no list changes.
/// - `.networkError(message)`: transport/decoding error with a localized
///   message.
///
/// `Equatable` so the service and view-model tests can assert the exact case.
/// The associated `message` never contains credential material (SEC / NFR3).
public enum SellOutcome: Sendable, Equatable {
    case total(sold: Int)
    case partial(sold: Int, total: Int)
    case none(total: Int)
    case networkError(message: String)

    /// Map a typed transport result into a sell outcome.
    ///
    /// - A success classifies by the `sold`/`total` counts: `sold == total`
    ///   (and `total > 0`) → `.total`; `0 < sold < total` → `.partial`;
    ///   otherwise → `.none`. A `success == false` body with no sold players is
    ///   `.none`.
    /// - Any transport/business failure (`unauthorized`, `forbidden`,
    ///   `clientError`, `server`, `transport`, `cancelled`, `decoding`,
    ///   `unexpectedStatus`) maps to `.networkError(genericNetwork)` — the typed
    ///   `NetworkError` carries no backend prose to quote, so the localized
    ///   generic notice is used (never a token or raw error description).
    public static func from(
        result: Result<SellResponse, NetworkError>,
        genericNetwork: String
    ) -> SellOutcome {
        switch result {
        case .success(let response):
            // A rejected body (success=false) with nothing sold is a "none".
            guard response.success || response.sold > 0 else {
                return .none(total: response.total)
            }
            let total = response.total
            let sold = response.sold
            if sold <= 0 {
                return .none(total: total)
            }
            if total > 0, sold >= total {
                return .total(sold: sold)
            }
            if sold < total {
                return .partial(sold: sold, total: total)
            }
            // total unknown/zero but something sold → treat as a full success.
            return .total(sold: sold)
        case .failure:
            return .networkError(message: genericNetwork)
        }
    }
}
