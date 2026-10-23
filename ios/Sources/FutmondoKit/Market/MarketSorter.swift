import Foundation

/// Pure, deterministic market sorting (FR5 / W3 / C6).
///
/// Rules:
/// - Always **descending** by the selected field.
/// - **Nulls last**: a player missing the sorted metric is placed after every
///   player that has it, regardless of direction.
/// - **Stable**: players comparing equal (including two nulls) keep their
///   relative input order, so reordering is predictable.
///
/// All fields map to a comparable `Double?` key so one algorithm covers both
/// the `Int?`/`Int` and `Double?` wire types.
public enum MarketSorter {
    /// Return `players` sorted descending by `field`, nulls last, stably.
    public static func sorted(
        _ players: [MarketPlayer],
        by field: MarketSortField
    ) -> [MarketPlayer] {
        // Decorate with the original index to make the sort stable (Swift's
        // `sorted(by:)` is not guaranteed stable).
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
    /// metric is absent and sorts last.
    private static func key(for player: MarketPlayer, field: MarketSortField) -> Double? {
        switch field {
        case .value:
            return Double(player.value)
        case .change:
            return player.change.map(Double.init)
        case .sofascoreRating:
            return player.sofascoreRating
        case .starterPct:
            return player.starterPct.map(Double.init)
        case .suggestedBid:
            return Double(player.suggestedBid)
        case .points:
            return player.points.map(Double.init)
        case .average:
            return player.average
        }
    }
}
