import Foundation

/// Persists only the active championship **id** (R5 / SR2). No session object
/// is ever stored here.
public protocol ActiveChampionshipStore: Sendable {
    var activeId: String? { get }
    func setActive(_ id: String)
}

/// `UserDefaults`-backed store. The key matches the web client for parity.
public final class UserDefaultsActiveChampionshipStore: ActiveChampionshipStore, @unchecked Sendable {
    /// Storage key (parity with the web app).
    public static let key = "futmondo_active_championship"

    private let defaults: UserDefaults

    public init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    public var activeId: String? {
        defaults.string(forKey: Self.key)
    }

    public func setActive(_ id: String) {
        defaults.set(id, forKey: Self.key)
    }
}
