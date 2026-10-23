import Foundation

/// Pure resolution of the active championship (R5 / FR3.2, FR3.3).
///
/// This function has **no side effects**: it does not touch `UserDefaults`.
/// Persisting the resolved id (when it differs from the stored one) is the
/// caller's responsibility — the `BudgetViewModel` (U2) owns FR3.3.
public enum ActiveChampionshipResolver {
    /// Resolve which championship should be active.
    ///
    /// - `activeId` matches an entry in `championships` → that entry.
    /// - `activeId` is `nil` or matches none → the first entry.
    /// - `championships` is empty → `nil`.
    public static func resolve(
        activeId: String?,
        in championships: [Championship]
    ) -> Championship? {
        guard !championships.isEmpty else {
            return nil
        }
        if let activeId,
           let match = championships.first(where: { $0.championshipId == activeId }) {
            return match
        }
        return championships.first
    }
}
