import Foundation

/// Typed, actionable network failures (NR3). This is the authoritative error
/// form and is `Equatable`: payloads are `Int` (status) or `String` (failure
/// mode message), never a raw `Error` (which is not `Equatable`) and never
/// credential material (SEC-N4).
public enum NetworkError: Error, Equatable {
    /// HTTP 401.
    case unauthorized
    /// HTTP 403.
    case forbidden
    /// Other 4xx (400, 404, 422, ...).
    case clientError(Int)
    /// HTTP 5xx.
    case server(Int)
    /// `CancellationError` — the caller must not retry (ADR-4).
    case cancelled
    /// Transport failure (offline, timeout, ...); carries a message derived
    /// solely from `error.localizedDescription`, never `userInfo` or the URL.
    case transport(String)
    /// Response body could not be decoded into the expected type.
    case decoding(String)
    /// 1xx/3xx or any other status not otherwise mapped.
    case unexpectedStatus(Int)
}
