import XCTest
@testable import FutmondoKit

/// Tests for the pure sort-key presentation metadata introduced for the F2
/// iteración 2b sort sheet (label + SF Symbol + display order). The SwiftUI
/// sheet that renders these is validated on device.
final class SortKeyPresentationTests: XCTestCase {

    // MARK: - 1. Display order covers all six keys, in canonical order

    func testDisplayOrderIsTheSixKeysInCanonicalOrder() {
        XCTAssertEqual(
            SortKey.displayOrder,
            [.balance, .performance, .maxBid, .teamValue, .totalSpent, .totalIncome]
        )
    }

    func testDisplayOrderCoversEveryCase() {
        XCTAssertEqual(Set(SortKey.displayOrder), Set(SortKey.allCases))
        XCTAssertEqual(SortKey.displayOrder.count, SortKey.allCases.count)
    }

    // MARK: - 2. Every key has a non-empty label and symbol

    func testEveryKeyHasNonEmptyLabelAndSymbol() {
        for key in SortKey.allCases {
            let p = key.presentation
            XCTAssertEqual(p.key, key)
            XCTAssertFalse(p.label.isEmpty, "label for \(key)")
            XCTAssertFalse(p.symbolName.isEmpty, "symbol for \(key)")
        }
    }

    // MARK: - 3. Labels match the interaction-spec Spanish text

    func testLabelsMatchSpec() {
        XCTAssertEqual(SortKey.balance.presentation.label, "Saldo")
        XCTAssertEqual(SortKey.performance.presentation.label, "Rendimiento")
        XCTAssertEqual(SortKey.maxBid.presentation.label, "Puja máxima")
        XCTAssertEqual(SortKey.teamValue.presentation.label, "Valor plantilla")
        XCTAssertEqual(SortKey.totalSpent.presentation.label, "Gastado")
        XCTAssertEqual(SortKey.totalIncome.presentation.label, "Ingresado")
    }

    // MARK: - 4. orderedPresentations aligns with displayOrder

    func testOrderedPresentationsAlignWithDisplayOrder() {
        XCTAssertEqual(SortKey.orderedPresentations.map(\.key), SortKey.displayOrder)
    }

    // MARK: - 5. Symbols are distinct per key

    func testSymbolsAreDistinct() {
        let symbols = SortKey.allCases.map { $0.presentation.symbolName }
        XCTAssertEqual(Set(symbols).count, symbols.count, "each key should map to a distinct SF Symbol")
    }
}
