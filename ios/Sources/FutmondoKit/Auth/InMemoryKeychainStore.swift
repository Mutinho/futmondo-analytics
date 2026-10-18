import Foundation

/// In-memory ``KeychainStore`` double for `swift test` (no `Security`
/// dependency, so it compiles on Linux/WSL).
///
/// Thread-safe via `NSLock` (portable across Darwin and
/// swift-corelibs-foundation), because `AuthService` is an actor and may touch
/// the store from concurrent tasks during the coalesced refresh. Tests can
/// optionally force `save`/`delete` to throw to exercise the REL-A4 path.
public final class InMemoryKeychainStore: KeychainStore, @unchecked Sendable {
    private let lock = NSLock()
    private var storedToken: String?

    /// When non-`nil`, `saveRefreshToken` throws this error (test hook).
    private var saveError: Error?
    /// When non-`nil`, `deleteRefreshToken` throws this error (test hook).
    private var deleteError: Error?

    public init(initialToken: String? = nil) {
        self.storedToken = initialToken
    }

    public func saveRefreshToken(_ token: String) throws {
        lock.lock()
        defer { lock.unlock() }
        if let saveError { throw saveError }
        storedToken = token
    }

    public func readRefreshToken() -> String? {
        lock.lock()
        defer { lock.unlock() }
        return storedToken
    }

    public func deleteRefreshToken() throws {
        lock.lock()
        defer { lock.unlock() }
        if let deleteError { throw deleteError }
        storedToken = nil
    }

    // MARK: - Test hooks

    /// Snapshot the stored token without going through `readRefreshToken`
    /// (keeps assertions explicit in tests).
    public func peekToken() -> String? {
        lock.lock()
        defer { lock.unlock() }
        return storedToken
    }

    /// Force the next `saveRefreshToken` calls to throw `error`.
    public func setSaveError(_ error: Error?) {
        lock.lock()
        defer { lock.unlock() }
        saveError = error
    }

    /// Force the next `deleteRefreshToken` calls to throw `error`.
    public func setDeleteError(_ error: Error?) {
        lock.lock()
        defer { lock.unlock() }
        deleteError = error
    }
}
