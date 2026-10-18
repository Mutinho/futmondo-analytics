import Foundation

/// An authenticated session. The access token lives only in memory (AR2); it
/// is never persisted.
public struct Session: Equatable, Sendable {
    public let accessToken: String
    public let user: UserMe

    public init(accessToken: String, user: UserMe) {
        self.accessToken = accessToken
        self.user = user
    }
}

/// Result of ``AuthService/bootstrap()`` (AR3 / REL-A1). `bootstrap` never
/// hangs: every network outcome maps to exactly one of these states.
public enum SessionState: Equatable, Sendable {
    /// A valid session was restored from the stored refresh token.
    case authenticated(Session)
    /// No valid session; the user must log in (no token, or a revoked token
    /// whose Keychain entry was cleared).
    case unauthenticated
    /// The refresh could not be confirmed because of a transport/server error;
    /// the stored refresh token is preserved and the attempt retries later.
    case offlinePreserved
}
