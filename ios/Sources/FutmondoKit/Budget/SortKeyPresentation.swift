import Foundation

/// Presentation metadata for a `SortKey`: its Spanish label, its SF Symbol
/// name, and the canonical display order of the six keys (F2 / iteración 2b —
/// the sort sheet). Kept as PURE logic in `FutmondoKit` so it is unit-testable
/// on Linux/WSL (`swift test`), away from the SwiftUI sheet that renders it.
///
/// `Sendable` because every stored value is a `String`/value type, so a
/// `static let` of these is concurrency-safe (Swift 6 strict concurrency).
public struct SortKeyPresentation: Sendable, Equatable {
    /// The sort key this metadata describes.
    public let key: SortKey
    /// Spanish label shown in the sort sheet row and the accessibility label.
    public let label: String
    /// SF Symbol name shown as the row's leading icon.
    public let symbolName: String

    public init(key: SortKey, label: String, symbolName: String) {
        self.key = key
        self.label = label
        self.symbolName = symbolName
    }
}

extension SortKey {
    /// Presentation metadata for this key (label + SF Symbol).
    public var presentation: SortKeyPresentation {
        switch self {
        case .balance:
            return SortKeyPresentation(key: self, label: "Saldo", symbolName: "eurosign.circle")
        case .performance:
            return SortKeyPresentation(key: self, label: "Rendimiento", symbolName: "chart.line.uptrend.xyaxis")
        case .maxBid:
            return SortKeyPresentation(key: self, label: "Puja máxima", symbolName: "gauge.with.needle")
        case .teamValue:
            return SortKeyPresentation(key: self, label: "Valor plantilla", symbolName: "person.3")
        case .totalSpent:
            return SortKeyPresentation(key: self, label: "Gastado", symbolName: "arrow.up.circle")
        case .totalIncome:
            return SortKeyPresentation(key: self, label: "Ingresado", symbolName: "arrow.down.circle")
        }
    }

    /// The six keys in canonical display order (saldo, rendimiento, puja
    /// máxima, valor plantilla, gastado, ingresado), matching the
    /// interaction-spec. Drives the sort sheet rows.
    public static let displayOrder: [SortKey] = [
        .balance, .performance, .maxBid, .teamValue, .totalSpent, .totalIncome,
    ]

    /// Presentation metadata for all six keys in display order.
    public static let orderedPresentations: [SortKeyPresentation] =
        displayOrder.map { $0.presentation }
}
