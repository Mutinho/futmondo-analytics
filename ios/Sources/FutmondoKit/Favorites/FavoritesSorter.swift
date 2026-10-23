import Foundation

/// The five metrics the Favoritos list can be sorted by (FR4 / W3 / BR4.1).
/// Sorting is ALWAYS descending with nulls last; the default is `.value`. The
/// raw value is a stable token persisted in `UserDefaults`
/// (``FavoritesPreferences``).
public enum FavoritesSortField: String, Sendable, CaseIterable, Equatable {
    case value
    case change
    case sofascoreRating
    case starterPct
    case points

    /// The default sort applied on first load (BR4.1).
    public static let defaultField: FavoritesSortField = .value
}

/// Pure, deterministic sorting of the favourites list (FR4 / W3 / BR4.1).
///
/// Rules (mirroring ``CalculatorSorter`` / ``MarketSorter``):
/// - Always **descending** by the selected field.
/// - **Nulls last**: a player missing the sorted metric is placed after every
///   player that has it.
/// - **Stable**: players comparing equal keep their relative input order.
///
/// The badge/sort rating is `sofascoreRating` (BR3.3), never the informative
/// `rating` field.
public enum FavoritesSorter {
    /// Return `players` sorted descending by `field`, nulls last, stably.
    public static func sorted(
        _ players: [FavoritePlayer],
        by field: FavoritesSortField
    ) -> [FavoritePlayer] {
        let decorated = players.enumerated().map { (index: $0.offset, player: $0.element) }

        let ordered = decorated.sorted { lhs, rhs in
            let lKey = key(for: lhs.player, field: field)
            let rKey = key(for: rhs.player, field: field)

            switch (lKey, rKey) {
            case let (l?, r?):
                if l == r {
                    return lhs.index < rhs.index // stable tie-break
                }
                return l > r // descending
            case (nil, nil):
                return lhs.index < rhs.index // stable tie-break among nulls
            case (_?, nil):
                return true // a present value precedes a null
            case (nil, _?):
                return false // a null follows a present value
            }
        }

        return ordered.map(\.player)
    }

    /// Project a player onto the comparable key for `field`. A `nil` means the
    /// metric is absent and sorts last. `value` is always present (required);
    /// the other fields are nullable.
    private static func key(
        for player: FavoritePlayer,
        field: FavoritesSortField
    ) -> Double? {
        switch field {
        case .value:
            return Double(player.value)
        case .change:
            return player.change.map(Double.init)
        case .sofascoreRating:
            return player.sofascoreRating
        case .starterPct:
            return player.starterPct.map(Double.init)
        case .points:
            return player.points.map(Double.init)
        }
    }
}
