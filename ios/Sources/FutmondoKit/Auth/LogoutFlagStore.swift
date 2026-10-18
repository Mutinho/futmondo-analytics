import Foundation

/// Persistence for the single boolean "logout revocation pending" flag (AR5 /
/// REL-A3). Abstracted behind a `Sendable` protocol so `AuthService` (an actor)
/// never has to hold a non-`Sendable` `UserDefaults` across its isolation
/// boundary, and so tests can inject an in-memory double.
///
/// Only the boolean flag is ever stored here — never the refresh token, which
/// stays solely in the Keychain (AR5 / ADR-2).
public protocol LogoutFlagStore: Sendable {
    func pendingLogoutRevocation() -> Bool
    func setPendingLogoutRevocation(_ pending: Bool)
}

/// `UserDefaults`-backed ``LogoutFlagStore``. `UserDefaults` is documented as
/// thread-safe, so the `@unchecked Sendable` box is sound; it is confined to
/// this type rather than leaking into the actor's stored state.
public final class UserDefaultsLogoutFlagStore: LogoutFlagStore, @unchecked Sendable {
    private let defaults: UserDefaults
    private let key: String

    public init(
        defaults: UserDefaults = .standard,
        key: String = "com.futmondo.app.auth.pendingLogoutRevocation"
    ) {
        self.defaults = defaults
        self.key = key
    }

    public func pendingLogoutRevocation() -> Bool {
        defaults.bool(forKey: key)
    }

    public func setPendingLogoutRevocation(_ pending: Bool) {
        defaults.set(pending, forKey: key)
    }
}

/// In-memory ``LogoutFlagStore`` for `swift test` (thread-safe via `NSLock`).
public final class InMemoryLogoutFlagStore: LogoutFlagStore, @unchecked Sendable {
    private let lock = NSLock()
    private var pending: Bool

    public init(pending: Bool = false) {
        self.pending = pending
    }

    public func pendingLogoutRevocation() -> Bool {
        lock.lock()
        defer { lock.unlock() }
        return pending
    }

    public func setPendingLogoutRevocation(_ pending: Bool) {
        lock.lock()
        defer { lock.unlock() }
        self.pending = pending
    }
}
