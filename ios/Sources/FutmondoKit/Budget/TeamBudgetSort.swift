import Foundation

/// Sorts a `TeamBudget` list descending by a `SortKey` (R2 / FR2.1).
///
/// The sort is **stable** (ties keep their relative input order) and
/// **non-mutating** (the input array is not changed; a new array is returned).
public enum TeamBudgetSort {
    public static func sorted(_ teams: [TeamBudget], by key: SortKey) -> [TeamBudget] {
        // `enumerated()` carries each element's original index so we can break
        // ties by it, which makes the descending sort stable (Swift's `sort`
        // is not guaranteed stable on its own).
        return teams.enumerated()
            .sorted { lhs, rhs in
                let left = metric(lhs.element, key)
                let right = metric(rhs.element, key)
                if left != right {
                    return left > right          // descending by the metric
                }
                return lhs.offset < rhs.offset   // stable tie-break
            }
            .map(\.element)
    }

    private static func metric(_ team: TeamBudget, _ key: SortKey) -> Int {
        switch key {
        case .balance: return team.balance
        case .performance: return team.performance
        case .maxBid: return team.maxBid
        case .teamValue: return team.teamValue
        case .totalSpent: return team.totalSpent
        case .totalIncome: return team.totalIncome
        }
    }
}
