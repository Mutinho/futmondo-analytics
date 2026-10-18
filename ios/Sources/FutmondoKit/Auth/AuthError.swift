import Foundation

/// Retroactive `Sendable` conformance for the Bolt 2 ``EmptyResponse`` marker.
///
/// `EmptyResponse` has no stored properties, so it is trivially concurrency-safe.
/// `AuthService` (an actor) uses it as the decode type for `POST /auth/logout`
/// (a 204/empty success). Declaring the conformance here keeps the reviewed
/// Bolt 2 source (`APIRequest.swift`) byte-stable.
extension EmptyResponse: @unchecked Sendable {}

/// `Sendable` conformance for the Bolt 2 ``UserMe`` value (immutable `String`
/// fields only). Declared here so `Session` (returned across the `AuthService`
/// actor boundary) is `Sendable` without editing the reviewed `UserMe.swift`.
extension UserMe: @unchecked Sendable {}

/// `Sendable` conformance for the Bolt 2 ``NetworkError`` (only `Int`/`String`
/// payloads). `AuthError.network(_)` wraps it and crosses the actor boundary.
extension NetworkError: @unchecked Sendable {}

/// Domain-level auth failures (AR1). `Equatable` so tests assert the exact
/// failure mode; carries no credential material.
public enum AuthError: Error, Equatable, Sendable {
    /// HTTP 401 on login: wrong email/password.
    case invalidCredentials
    /// An underlying transport/server/decoding failure from the network layer.
    case network(NetworkError)
    /// The refresh flow could not mint a new access token.
    case refreshFailed
    /// Any other unexpected condition, with a non-sensitive message.
    case unknown(String)
}
