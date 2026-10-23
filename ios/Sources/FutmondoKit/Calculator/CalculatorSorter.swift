import Foundation

/// The four metrics the Calculadora selectable list can be sorted by (FR5.3 /
/// W7). Sorting is ALWAYS descending with nulls last; the default is
/// `.projectedValue`. The raw value is a stable token persisted in
/// `UserDefaults` (CalculatorPreferences).
public enum CalculatorSortField: String, Sendable, CaseIterable, Equatable {
    case projectedValue = "projectedValue"
    case value
    case change
    case profit

    /// The default sort applied on first load (BR5.1).
    public static let defaultField: CalculatorSortField = .projectedValue
}

/// Pure, deterministic sorting of the selectable roster (FR5.3 / W7 / BR7.1).
///
/// Rules (mirroring ``MarketSorter``):
/// - Always **descending** by the selected field.
/// - **Nulls last**: a player missing the sorted metric is placed after every
///   player that has it.
/// - **Stable**: players comparing equal keep their relative input order.
///
/// `projectedValue` depends on `daysAhead` (BR1.1), so it is passed in. The
/// other fields ignore it. `profit` is the presentation-only plusvalía (BR7.1);
/// sorting by it never affects the money invariants.
public enum CalculatorSorter {
    /// Return `players` sorted descending by `field`, nulls last, stably.
    public static func sorted(
        _ players: [RosterPlayer],
        by field: CalculatorSortField,
        daysAhead: Int
    ) -> [RosterPlayer] {
        let decorated = players.enumerated().map { (index: $0.offset, player: $0.element) }

        let ordered = decorated.sorted { lhs, rhs in
            let lKey = key(for: lhs.player, field: field, daysAhead: daysAhead)
            let rKey = key(for: rhs.player, field: field, daysAhead: daysAhead)

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
    /// metric is absent and sorts last. `projectedValue` and `value` are always
    /// present (computed from the required `value`); `change` and `profit` are
    /// nullable.
    private static func key(
        for player: RosterPlayer,
        field: CalculatorSortField,
        daysAhead: Int
    ) -> Double? {
        switch field {
        case .projectedValue:
            return Double(CalculatorMath.projectedValue(player, daysAhead: daysAhead))
        case .value:
            return Double(player.value)
        case .change:
            return player.change.map(Double.init)
        case .profit:
            return player.profit.map(Double.init)
        }
    }
}
