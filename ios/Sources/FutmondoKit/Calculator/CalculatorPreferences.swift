import Foundation

/// The persisted preferences of the Calculadora (entities.md
/// `CalculatorPreferences`): the "incorporar en venta" toggle and the sort
/// field. Stored in `UserDefaults` (non-sensitive, NFR7).
///
/// `UserDefaults` is injected through the ``KeyValueStore`` abstraction so the
/// policy is unit-tested on Linux/WSL with an in-memory double (no real
/// `UserDefaults` needed).
///
/// `includeOnSale` default is ON (BR5.1): any stored value that is NOT the
/// literal `"false"` resolves to ON — including an absent value. This mirrors
/// the Angular web behaviour exactly.
public struct CalculatorPreferences {
    /// Keys used in the backing store.
    public enum Key {
        public static let includeOnSale = "calculator.includeOnSale"
        public static let sortField = "calculator.sortField"
    }

    private let store: any KeyValueStore

    public init(store: any KeyValueStore) {
        self.store = store
    }

    /// The persisted "incorporar en venta" toggle (BR5.1). Default ON: only the
    /// exact literal `"false"` resolves to OFF; an absent value or any other
    /// string is ON.
    public var includeOnSale: Bool {
        get {
            guard let stored = store.string(forKey: Key.includeOnSale) else { return true }
            return stored != "false"
        }
        nonmutating set {
            store.setString(newValue ? "true" : "false", forKey: Key.includeOnSale)
        }
    }

    /// The persisted sort field (FR5.3). Defaults to `.projectedValue` when
    /// absent or unrecognized.
    public var sortField: CalculatorSortField {
        get {
            guard let raw = store.string(forKey: Key.sortField),
                  let field = CalculatorSortField(rawValue: raw) else {
                return .defaultField
            }
            return field
        }
        nonmutating set {
            store.setString(newValue.rawValue, forKey: Key.sortField)
        }
    }
}

/// Minimal string key-value store so ``CalculatorPreferences`` is testable
/// without a real `UserDefaults`. Use ``UserDefaultsKeyValueStore`` on device
/// (a thin wrapper, since `UserDefaults` itself is not `Sendable`), and
/// ``InMemoryKeyValueStore`` in tests/previews.
public protocol KeyValueStore {
    func string(forKey defaultName: String) -> String?
    func setString(_ value: String?, forKey defaultName: String)
}

/// `UserDefaults`-backed ``KeyValueStore`` (device/app use). A thin wrapper
/// rather than a direct `UserDefaults` conformance because `UserDefaults` is
/// not `Sendable` and its `set` takes `Any?`, not `String?`.
public struct UserDefaultsKeyValueStore: KeyValueStore {
    private let defaults: UserDefaults

    public init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    public func string(forKey defaultName: String) -> String? {
        defaults.string(forKey: defaultName)
    }

    public func setString(_ value: String?, forKey defaultName: String) {
        defaults.set(value, forKey: defaultName)
    }
}

/// In-memory ``KeyValueStore`` double for tests and previews. Thread-safe via a
/// lock so it is `Sendable` under Swift 6 strict concurrency.
public final class InMemoryKeyValueStore: KeyValueStore, @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: String]

    public init(initial: [String: String] = [:]) {
        self.storage = initial
    }

    public func string(forKey defaultName: String) -> String? {
        lock.lock(); defer { lock.unlock() }
        return storage[defaultName]
    }

    public func setString(_ value: String?, forKey defaultName: String) {
        lock.lock(); defer { lock.unlock() }
        if let value {
            storage[defaultName] = value
        } else {
            storage.removeValue(forKey: defaultName)
        }
    }
}
