import Foundation

/// The seven metrics the market list can be sorted by (FR5 / W3 / C6). Sorting
/// is ALWAYS descending with nulls last; the default is `.value`. The raw value
/// matches the Angular `sortField` tokens for parity.
public enum MarketSortField: String, Sendable, CaseIterable, Equatable {
    case value
    case change
    case sofascoreRating = "sofascore_rating"
    case starterPct = "starter_pct"
    case suggestedBid = "suggested_bid"
    case points
    case average

    /// The default sort applied on first load (W1/W3).
    public static let defaultField: MarketSortField = .value
}
