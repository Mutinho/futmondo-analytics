import Foundation

/// Construction-time failures for a network client (distinct from per-request
/// ``NetworkError``). A thrown error is not eliminable by `-Ounchecked`, unlike
/// a `precondition` (SEC-N1).
public enum NetworkClientError: Error, Equatable {
    /// The base URL scheme was not `https`.
    case insecureBaseURL
}

/// Typed HTTP transport contract. Implementations map every outcome to a
/// `Result<T, NetworkError>` and never throw from `send` (NR3).
///
/// `Sendable`: the contract is stateless and its implementations are safe to
/// pass across the `AuthService` actor boundary (Swift 6 strict concurrency).
public protocol NetworkClient: Sendable {
    func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError>
}
