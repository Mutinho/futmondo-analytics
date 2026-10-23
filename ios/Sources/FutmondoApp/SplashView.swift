import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Auto-login splash (C5 / AR3 / AR6). On appear it runs
/// `AuthService.bootstrap()` and routes to the authenticated surface, to login,
/// or shows a brief offline banner then falls through to login — it never
/// hangs. The logo shares a `matchedGeometryEffect` with ``LoginView``.
@available(iOS 17.0, macOS 14.0, *)
public struct SplashView: View {
    /// Local splash phase mirroring the interaction-spec states.
    public enum Phase: Equatable {
        case checking
        case resumed
        case expired
        case offline
        case noSession
    }

    private let authService: AuthService
    private let networkClient: NetworkClient
    @State private var viewModel: AuthViewModel
    @State private var budgetViewModel: BudgetViewModel
    @State private var marketViewModel: MarketViewModel
    @State private var calculatorViewModel: CalculatorViewModel
    @State private var favoritesViewModel: FavoritesViewModel
    /// Shared F2 budget collaborators, built once over the SAME HTTPS client as
    /// auth (AR8 / SEC-N1) and reused to compose the pushed team-detail view
    /// model (FR6) so the detail hits the same transport + active championship.
    private let budgetService: any BudgetService
    private let activeStore: any ActiveChampionshipStore
    /// Shared F3 market collaborator for the Sofascore detail (FR8), over the
    /// SAME HTTPS client + active store, so a fresh isolated detail VM can be
    /// built per opened sheet.
    private let sofascoreService: any SofascoreService
    @State private var phase: Phase = .checking
    @Namespace private var logoNamespace
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(authService: AuthService, networkClient: NetworkClient) {
        self.authService = authService
        self.networkClient = networkClient
        _viewModel = State(initialValue: AuthViewModel(authService: authService))
        // Compose the F2 budget view model over the SAME HTTPS NetworkClient as
        // auth (AR8 / SEC-N1): no second, insecure client is ever created. The
        // budget service + active store are retained so the team-detail view
        // model (FR6) reuses them.
        let sharedBudgetService = HTTPBudgetService(network: networkClient)
        let sharedActiveStore = UserDefaultsActiveChampionshipStore()
        self.budgetService = sharedBudgetService
        self.activeStore = sharedActiveStore
        let budget = BudgetViewModel(
            budgetService: sharedBudgetService,
            championshipService: HTTPChampionshipService(network: networkClient),
            activeStore: sharedActiveStore
        )
        _budgetViewModel = State(initialValue: budget)
        // Compose the F3 market view model + Sofascore service over the SAME
        // HTTPS NetworkClient + active store (AR8 / SEC-N1 / FR8.2).
        let sharedSofascoreService = HTTPSofascoreService(network: networkClient)
        self.sofascoreService = sharedSofascoreService
        let market = MarketViewModel(
            marketService: HTTPMarketService(network: networkClient),
            activeStore: sharedActiveStore,
            // After an accepted bid/cancel the economy figures change, so the
            // budget screen's cached data is now stale: invalidate it (both VMs
            // share the active-championship store) so it refetches when shown.
            onWriteAccepted: { [weak budget] in budget?.invalidate() }
        )
        _marketViewModel = State(initialValue: market)
        // Compose the F4 calculadora view model over the SAME HTTPS transport +
        // active store, plus a `RosterService` for roster/on-sale/sell/cancel
        // and the persisted `CalculatorPreferences`. After an accepted
        // sell/cancel the shared economy changes, so it invalidates BOTH the
        // budget and the market caches (BR10.1 / FR10.1).
        _calculatorViewModel = State(initialValue: CalculatorViewModel(
            rosterService: HTTPRosterService(network: networkClient),
            marketService: HTTPMarketService(network: networkClient),
            activeStore: sharedActiveStore,
            preferences: CalculatorPreferences(store: UserDefaultsKeyValueStore()),
            onWriteAccepted: { [weak budget, weak market] in
                budget?.invalidate()
                market?.invalidate()
            }
        ))
        // Compose the F5 favoritos view model over the SAME HTTPS transport +
        // active store, plus a `FavoritesService` and the persisted
        // `FavoritesPreferences`. Unfollowing a favourite does not change the
        // shared economy figures, so it needs NO cross-screen invalidation
        // (FR7.1) — it owns no `onWriteAccepted` callback.
        _favoritesViewModel = State(initialValue: FavoritesViewModel(
            favoritesService: HTTPFavoritesService(network: networkClient),
            activeStore: sharedActiveStore,
            preferences: FavoritesPreferences(store: UserDefaultsKeyValueStore())
        ))
    }

    public var body: some View {
        content
            .animation(reduceMotion ? nil : .default, value: phase)
            .task { await runBootstrap() }
            // Manual login success (from LoginView) must route to the
            // authenticated surface: bootstrap only runs at launch, so without
            // this the view would stay on the login form after a successful
            // login (AR1/AR6). Logout resets the ViewModel to .idle, which must
            // NOT bounce back to the login form here.
            .onChange(of: viewModel.state) { _, newState in
                if newState == .success { phase = .resumed }
            }
    }

    @ViewBuilder
    private var content: some View {
        switch phase {
        case .checking:
            checkingView
        case .resumed:
            // F2 authenticated surface: the budget screen inside a tabbed root.
            // The logout closure runs the SAME F1 seam as the old placeholder
            // (AuthViewModel.logout() + phase = .noSession); session logic is
            // untouched.
            RootTabView(viewModel: budgetViewModel, marketViewModel: marketViewModel, calculatorViewModel: calculatorViewModel, favoritesViewModel: favoritesViewModel) {
                Task {
                    await viewModel.logout()
                    phase = .noSession
                }
            } makeTeamDetailViewModel: {
                // A fresh VM per pushed detail, over the shared budget service +
                // active store (same HTTPS transport as the list, AR8/SEC-N1).
                TeamDetailViewModel(
                    budgetService: budgetService,
                    activeStore: activeStore
                )
            } makeSofascoreViewModel: {
                // A fresh, isolated VM per opened Sofascore sheet (FR8.2), over
                // the shared Sofascore service + active store.
                SofascoreDetailViewModel(
                    service: sofascoreService,
                    activeStore: activeStore
                )
            }
        case .offline:
            VStack(spacing: 16) {
                logo
                offlineBanner
                LoginView(viewModel: viewModel, logoNamespace: logoNamespace)
            }
        case .expired, .noSession:
            VStack(spacing: 16) {
                logo
                LoginView(viewModel: viewModel, logoNamespace: logoNamespace)
            }
        }
    }

    private var checkingView: some View {
        VStack(spacing: 16) {
            logo
            ProgressView()
            Text("Recuperando sesión…")
                .font(.callout)
                .foregroundStyle(.secondary)
        }
        .accessibilityElement(children: .combine)
    }

    private var offlineBanner: some View {
        Text("Sin conexión. Inicia sesión cuando vuelvas a tener red.")
            .font(.callout)
            .foregroundStyle(.secondary)
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.yellow.opacity(0.15), in: RoundedRectangle(cornerRadius: 10))
    }

    private var logo: some View {
        Image(systemName: "sportscourt.fill")
            .resizable()
            .scaledToFit()
            .frame(width: 72, height: 72)
            .matchedGeometryEffect(id: "logo", in: logoNamespace)
            .accessibilityHidden(true)
    }

    private func runBootstrap() async {
        let state = await authService.bootstrap()
        switch state {
        case .authenticated:
            phase = .resumed
        case .unauthenticated:
            phase = .noSession
        case .offlinePreserved:
            phase = .offline
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
