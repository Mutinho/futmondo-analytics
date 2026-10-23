import Foundation

/// Decoded body of a 2xx bid / cancel-bid response (FR6.4 / FR7.3).
///
/// The backend returns `{ "success": true|false, ... }` on a 2xx; a
/// `success == false` body is a business rejection (e.g. Futmondo refused the
/// bid) and carries a human message in `message` or `detail`. Both are optional
/// and either may be present. All fields beyond these are ignored.
public struct MarketWriteResponse: Codable, Sendable, Equatable {
    public let success: Bool
    public let message: String?
    public let detail: String?

    public init(success: Bool, message: String? = nil, detail: String? = nil) {
        self.success = success
        self.message = message
        self.detail = detail
    }

    /// The best available human-facing message for a rejection, or `nil` when
    /// the backend sent none (the view model then uses a generic notice). Never
    /// carries credential material — it is only the backend's own prose.
    public var rejectionMessage: String? {
        if let message, !message.isEmpty { return message }
        if let detail, !detail.isEmpty { return detail }
        return nil
    }
}

/// The three mutually exclusive outcomes of a market write (bid or cancel),
/// per W6 / FR6.4 / FR7.3 / ADR-2 ("never a silent bool/nil").
///
/// - `.accepted`: HTTP 2xx with `success == true`. The view model shows a
///   success notice and reloads the market (BR-UI-3).
/// - `.rejected(message)`: HTTP 2xx with `success == false`, or a 4xx (422
///   invalid price / 400 no team). The view model shows `message` (the
///   backend's own text, or a generic fallback) and does NOT reload.
/// - `.networkError`: a transport failure or a 5xx. The view model shows a
///   generic error notice and does NOT reload.
///
/// `Equatable` so the view-model and service tests can assert the exact case.
/// The associated `message` never contains credential material (SEC / NFR3).
public enum MarketWriteOutcome: Sendable, Equatable {
    case accepted
    case rejected(message: String)
    case networkError

    /// Map a typed transport result into a write outcome.
    ///
    /// - A success decodes to `.accepted` when `success == true`, else
    ///   `.rejected` with the backend's message (or `fallbackRejection`).
    /// - A `.clientError`/`.unauthorized`/`.forbidden` (4xx) is a business
    ///   rejection → `.rejected` (with `fallbackRejection`, since the typed
    ///   `NetworkError` carries no backend body to quote).
    /// - A `.server` (5xx), `.transport`, `.cancelled`, `.decoding`, or
    ///   `.unexpectedStatus` is a `.networkError`.
    ///
    /// `fallbackRejection` and `genericNetwork` are caller-supplied, localized
    /// (Spanish) notices so no English leaks into the UI and no credential
    /// material is ever synthesized here.
    public static func from(
        result: Result<MarketWriteResponse, NetworkError>,
        fallbackRejection: String,
        genericNetwork: String
    ) -> MarketWriteOutcome {
        switch result {
        case .success(let response):
            if response.success {
                return .accepted
            }
            return .rejected(message: response.rejectionMessage ?? fallbackRejection)
        case .failure(let error):
            switch error {
            case .unauthorized, .forbidden, .clientError:
                // 4xx: a business rejection. The typed error has no backend
                // prose to quote, so use the localized fallback.
                return .rejected(message: fallbackRejection)
            case .server, .transport, .cancelled, .decoding, .unexpectedStatus:
                return .networkError
            }
        }
    }
}
