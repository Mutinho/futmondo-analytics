import Foundation

/// The metric a `TeamBudget` list can be sorted by (always descending).
public enum SortKey: Sendable, CaseIterable {
    case balance
    case performance
    case maxBid
    case teamValue
    case totalSpent
    case totalIncome
}
