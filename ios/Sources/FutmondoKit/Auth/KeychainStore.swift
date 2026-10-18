import Foundation

/// Secure store contract for the refresh token (SEC-A1 / AR2).
///
/// `AuthService` depends on this protocol so tests can inject an in-memory
/// double; the production implementation (`KeychainTokenStore`) is backed by
/// Keychain Services and only compiles where `Security` is available.
///
/// The refresh token is the only credential this store ever holds. The access
/// token stays in memory (``AuthService`` + ``TokenHolder``) and is never
/// persisted (AR2).
///
/// `Sendable`: implementations are safe to pass across the `AuthService` actor
/// boundary (Swift 6 strict concurrency).
public protocol KeychainStore: Sendable {
    /// Persist (upsert) the refresh token. Propagates on an underlying failure
    /// (REL-A4) rather than silently assuming success.
    func saveRefreshToken(_ token: String) throws

    /// Read the stored refresh token, or `nil` when none is stored.
    func readRefreshToken() -> String?

    /// Remove the stored refresh token. A missing item is not an error.
    func deleteRefreshToken() throws
}
