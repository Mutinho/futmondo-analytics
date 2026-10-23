import Foundation

/// The persisted preferences of the Favoritos screen (entities.md
/// `FavoritesPreferences`): only the sort field. Stored in `UserDefaults`
/// (non-sensitive, NFR7).
///
/// `UserDefaults` is injected through the shared ``KeyValueStore`` abstraction
/// (defined with ``CalculatorPreferences``) so the policy is unit-tested on
/// Linux/WSL with an in-memory double (no real `UserDefaults` needed).
public struct FavoritesPreferences {
    /// Keys used in the backing store.
    public enum Key {
        public static let sortField = "favorites.sortField"
    }

    private let store: any KeyValueStore

    public init(store: any KeyValueStore) {
        self.store = store
    }

    /// The persisted sort field (FR4 / BR4.1). Defaults to `.value` when absent
    /// or unrecognized.
    public var sortField: FavoritesSortField {
        get {
            guard let raw = store.string(forKey: Key.sortField),
                  let field = FavoritesSortField(rawValue: raw) else {
                return .defaultField
            }
            return field
        }
        nonmutating set {
            store.setString(newValue.rawValue, forKey: Key.sortField)
        }
    }
}
