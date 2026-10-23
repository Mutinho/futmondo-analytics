import Foundation

/// Pure decision of whether the resolved active championship id must be
/// persisted (R5 / FR3.3).
///
/// This is the side-effect-free counterpart to ``ActiveChampionshipResolver``:
/// the resolver decides *which* championship is active, this decides *whether*
/// the caller (the `BudgetViewModel`, U2) has to write it back to the
/// ``ActiveChampionshipStore``. Keeping the rule here (not inside the
/// SwiftUI-bound view model) makes it unit-testable on Linux/WSL, where the
/// SwiftUI layer is device-validated instead.
public enum ActiveChampionshipPersistence {
    /// Whether `resolvedId` should be written to the store.
    ///
    /// Persist only when there is a resolved id AND it differs from the stored
    /// one. A `nil` resolved id (empty championship list) never persists, and a
    /// resolved id equal to the stored id is a no-op — so a transient failure
    /// that does not change the resolution cannot churn `UserDefaults`.
    ///
    /// - Parameters:
    ///   - resolvedId: the id ``ActiveChampionshipResolver`` resolved, or `nil`.
    ///   - storedId: the id currently held by the store, or `nil`.
    /// - Returns: `true` when the caller must call `setActive(resolvedId)`.
    public static func shouldPersist(resolvedId: String?, storedId: String?) -> Bool {
        guard let resolvedId else {
            return false
        }
        return resolvedId != storedId
    }
}
