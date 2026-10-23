import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Authenticated root surface (US4 / FR5.1). A native `TabView` with a single
/// "Presupuesto" tab wrapping a `NavigationStack(BudgetView)`.
///
/// D2 — Floating Liquid Glass tab bar: the package app target now deploys to
/// iOS 26, so the NATIVE `TabView` + `Tab` API renders with the iOS 26 floating
/// glass look automatically, with no custom effect. On iOS 18+ the `Tab(_:
/// systemImage:)` value-builder API is used; older runtimes fall back to the
/// `tabItem` modifier (the app ships iOS 26+, so this is defensive only).
///
/// It receives the composed `BudgetViewModel` and a logout closure; the closure
/// runs the F1 `AuthViewModel.logout()` + `phase = .noSession` seam owned by
/// `SplashView` (this view never touches session logic directly). The logout
/// affordance itself lives in `BudgetView`'s settings/overflow menu (D5).
///
/// F3 adds the 2nd "Mercado" tab (`MarketView`) beside Presupuesto, each in its
/// own `NavigationStack`. The market collaborators are injected from the
/// composition root so the market reuses the SAME HTTPS transport +
/// active-championship store as the budget list.
@available(iOS 17.0, macOS 14.0, *)
public struct RootTabView: View {
    private let viewModel: BudgetViewModel
    private let marketViewModel: MarketViewModel
    private let calculatorViewModel: CalculatorViewModel
    private let favoritesViewModel: FavoritesViewModel
    private let onLogout: () -> Void
    /// Factory for a pushed team-detail view model (FR6), forwarded to
    /// `BudgetView`. Built at the composition root so the detail reuses the
    /// same HTTPS transport + active-championship store as the list.
    private let makeTeamDetailViewModel: () -> TeamDetailViewModel
    /// Factory for a fresh Sofascore detail view model per opened sheet (FR8),
    /// forwarded to `MarketView` and `FavoritesView` so each sheet's state is
    /// isolated (FR8.2).
    private let makeSofascoreViewModel: () -> SofascoreDetailViewModel

    public init(
        viewModel: BudgetViewModel,
        marketViewModel: MarketViewModel,
        calculatorViewModel: CalculatorViewModel,
        favoritesViewModel: FavoritesViewModel,
        onLogout: @escaping () -> Void,
        makeTeamDetailViewModel: @escaping () -> TeamDetailViewModel,
        makeSofascoreViewModel: @escaping () -> SofascoreDetailViewModel
    ) {
        self.viewModel = viewModel
        self.marketViewModel = marketViewModel
        self.calculatorViewModel = calculatorViewModel
        self.favoritesViewModel = favoritesViewModel
        self.onLogout = onLogout
        self.makeTeamDetailViewModel = makeTeamDetailViewModel
        self.makeSofascoreViewModel = makeSofascoreViewModel
    }

    public var body: some View {
        tabView
            // Selected-tab colour: the DesignSystem green (DSColor.primary,
            // #66BB6A in dark) instead of the system blue. Accessibility is
            // preserved because selection is also conveyed by the filled icon +
            // label (not colour alone), and the green token meets contrast.
            .tint(DSColor.primary)
    }

    @ViewBuilder
    private var tabView: some View {
        if #available(iOS 18.0, macOS 15.0, *) {
            TabView {
                Tab("Presupuesto", systemImage: "eurosign.circle") {
                    budgetTab
                }
                Tab("Mercado", systemImage: "cart") {
                    marketTab
                }
                Tab("Calculadora", systemImage: "plusminus.circle") {
                    calculatorTab
                }
                Tab("Favoritos", systemImage: "star") {
                    favoritesTab
                }
            }
        } else {
            TabView {
                budgetTab
                    .tabItem {
                        Label("Presupuesto", systemImage: "eurosign.circle")
                    }
                marketTab
                    .tabItem {
                        Label("Mercado", systemImage: "cart")
                    }
                calculatorTab
                    .tabItem {
                        Label("Calculadora", systemImage: "plusminus.circle")
                    }
                favoritesTab
                    .tabItem {
                        Label("Favoritos", systemImage: "star")
                    }
            }
        }
    }

    private var budgetTab: some View {
        NavigationStack {
            BudgetView(
                viewModel: viewModel,
                onLogout: onLogout,
                makeTeamDetailViewModel: makeTeamDetailViewModel
            )
        }
    }

    private var marketTab: some View {
        NavigationStack {
            MarketView(
                viewModel: marketViewModel,
                budgetViewModel: viewModel,
                onLogout: onLogout,
                makeSofascoreViewModel: makeSofascoreViewModel
            )
        }
    }

    private var calculatorTab: some View {
        NavigationStack {
            CalculatorView(
                viewModel: calculatorViewModel,
                budgetViewModel: viewModel,
                onLogout: onLogout
            )
        }
    }

    private var favoritesTab: some View {
        NavigationStack {
            FavoritesView(
                viewModel: favoritesViewModel,
                budgetViewModel: viewModel,
                onLogout: onLogout,
                makeSofascoreViewModel: makeSofascoreViewModel
            )
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
