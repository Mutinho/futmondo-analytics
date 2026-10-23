import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Sort-key selector (US3 / FR2.1), rendered as a GLASS icon-button in the
/// navigation bar that opens a NATIVE `Menu` (the iOS contextual "bubble"),
/// homogeneous with the trophy championship selector and the Mercado sort
/// control (owner decision 2026-10-21 — replaces the former bottom sheet so all
/// main screens share one mechanic).
///
/// Each of the six `SortKey` metrics is a menu item with its SF Symbol; the
/// active key carries a checkmark. Selecting a row calls `viewModel.setSort`.
@available(iOS 17.0, macOS 14.0, *)
public struct SortMenu: View {
    @Bindable private var viewModel: BudgetViewModel

    public init(viewModel: BudgetViewModel) {
        self.viewModel = viewModel
    }

    private var activeLabel: String { viewModel.sortKey.presentation.label }

    public var body: some View {
        Menu {
            ForEach(SortKey.orderedPresentations, id: \.key) { option in
                Button {
                    viewModel.setSort(option.key)
                } label: {
                    if option.key == viewModel.sortKey {
                        Label(option.label, systemImage: "checkmark")
                    } else {
                        Label(option.label, systemImage: option.symbolName)
                    }
                }
            }
        } label: {
            DSGlassIcon(systemImage: "arrow.up.arrow.down")
        }
        .accessibilityLabel("Ordenar por \(activeLabel), abre opciones")
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
