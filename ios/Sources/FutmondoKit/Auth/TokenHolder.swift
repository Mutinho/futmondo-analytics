import Foundation

/// Sendable snapshot of the in-memory access token (SEC-A2 / AR8).
///
/// The `NetworkClient` from Bolt 2 takes a **synchronous**
/// `accessTokenProvider: () -> String?`, which cannot enter the `AuthService`
/// actor inline. `TokenHolder` bridges that gap: `AuthService` writes the
/// current access token here on every change (login / refresh / logout), and
/// the provider reads it without touching the actor.
///
/// The lock is `NSLock` on purpose — it exists in both Darwin Foundation and
/// swift-corelibs-foundation — so this type compiles under `swift test` on
/// Linux/WSL. `OSAllocatedUnfairLock` is deliberately NOT used (iOS 16+/macOS
/// 13 only; absent on Linux, it would break the test build).
public final class TokenHolder: @unchecked Sendable {
    private let lock = NSLock()
    private var token: String?

    public init(token: String? = nil) {
        self.token = token
    }

    /// Read the current access token under the lock.
    public func get() -> String? {
        lock.lock()
        defer { lock.unlock() }
        return token
    }

    /// Replace the current access token under the lock. Passing `nil` cuts off
    /// `Bearer` injection immediately for any in-flight request reading the
    /// holder (used first in the logout teardown, SEC-A2 / AR5).
    public func set(_ newToken: String?) {
        lock.lock()
        defer { lock.unlock() }
        token = newToken
    }
}
