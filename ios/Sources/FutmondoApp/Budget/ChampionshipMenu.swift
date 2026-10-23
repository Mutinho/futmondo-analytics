import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Championship selector (US2 / FR3.1), rendered as a GLASS icon-button with a
/// TROPHY SF Symbol, placed in the navigation-bar LEADING position (F2 /
/// iteración 2b — replaces the former title chip in `.principal`). It mirrors
/// the trailing settings/overflow glass button so the nav bar is symmetric:
/// trophy (leading) — title — ellipsis (trailing).
///
/// A native `Menu` whose label is the `DSGlassIcon`. Each championship is a
/// menu item; the active one carries a checkmark. When the list is empty the
/// control is disabled and the icon is muted (`trophy` rather than
/// `trophy.fill`). Selecting an item calls `viewModel.selectChampionship`,
/// which persists and reloads.
@available(iOS 17.0, macOS 14.0, *)
public struct ChampionshipMenu: View {
    @Bindable private var viewModel: BudgetViewModel

    public init(viewModel: BudgetViewModel) {
        self.viewModel = viewModel
    }

    private var isEmpty: Bool { viewModel.championships.isEmpty }

    private var activeName: String {
        viewModel.activeChampionship?.name ?? "Sin campeonato"
    }

    public var body: some View {
        Menu {
            ForEach(viewModel.championships) { championship in
                // A native single-select `Toggle` per row: SwiftUI renders the
                // checkmark for the active one and reserves the SAME leading
                // gutter on every row, so the names all start at the same x
                // (a plain Text/Label mix left the unticked rows shifted). This
                // component is transversal — the fix lands on every screen that
                // shows the championship selector (Presupuesto, Mercado, …).
                Toggle(
                    isOn: Binding(
                        get: { championship.championshipId == viewModel.activeChampionship?.championshipId },
                        set: { selected in
                            if selected {
                                Task { await viewModel.selectChampionship(championship) }
                            }
                        }
                    )
                ) {
                    Text(championship.name)
                }
            }
        } label: {
            DSGlassIcon(
                systemImage: isEmpty ? "trophy" : "trophy.fill",
                isEnabled: !isEmpty
            )
        }
        .disabled(isEmpty)
        .accessibilityLabel("Campeonato activo: \(activeName), abre selector")
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
