import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Budget screen (US1 / FR1, FR4). Lives inside the `NavigationStack` provided
/// by `RootTabView`. The navigation bar reads (F2 / iteración 2b): a TROPHY
/// glass championship selector + a SORT glass button (leading) — the inline
/// title — the settings/overflow glass `Menu` with the logout item (trailing).
/// All three are symmetric glass icon buttons (`DSGlassIcon`); the former
/// title chip (`.principal`) and inline "Ordenar por" chip are removed.
///
/// The body switches on `BudgetState`:
/// - `.loading`  → `SkeletonScreen` (skeleton de carga)
/// - `.loaded`   → scrollable stack of elevated `BudgetRow` cards (D1)
/// - `.emptyTeams` → "Este campeonato no tiene equipos aún."
/// - `.noChampionships` → "No tienes campeonatos." (selector disabled)
/// - `.error`    → `ErrorState` + Reintentar (VoiceOver focus moved to it, NFR5)
///
/// The authenticated sporty background + legibility scrim is hosted here via
/// `.authenticatedBackground()` so the content surface is transparent above it.
@available(iOS 17.0, macOS 14.0, *)
public struct BudgetView: View {
    @Bindable private var viewModel: BudgetViewModel
    private let onLogout: () -> Void
    /// Builds a fresh `TeamDetailViewModel` for a pushed detail screen (FR6).
    /// Injected from the composition root so the detail reuses the SAME HTTPS
    /// transport + active-championship store as the list (AR8 / SEC-N1).
    private let makeTeamDetailViewModel: () -> TeamDetailViewModel

    /// Shared namespace for the iOS 18+ zoom navigation transition between a
    /// tapped `BudgetRow` card and its detail screen (FR6). Guarded at the use
    /// site; older runtimes fall back to a normal push.
    @Namespace private var zoomNamespace

    /// VoiceOver focus so an error moves focus to the Reintentar button (NFR5).
    @AccessibilityFocusState private var retryFocused: Bool

    public init(
        viewModel: BudgetViewModel,
        onLogout: @escaping () -> Void,
        makeTeamDetailViewModel: @escaping () -> TeamDetailViewModel
    ) {
        self.viewModel = viewModel
        self.onLogout = onLogout
        self.makeTeamDetailViewModel = makeTeamDetailViewModel
    }

    public var body: some View {
        CrossfadeLoader(isLoading: isLoadingState) {
            SkeletonListScreen(showHeader: true)
        } content: {
            content
        }
            .authenticatedBackground()
            .navigationTitle("Presupuesto")
            .navigationBarTitleDisplayMode(.large)
            .navigationDestination(for: TeamDetailRoute.self) { route in
                detailDestination(for: route)
            }
            .toolbar {
                // Leading group: trophy championship selector + sort control,
                // symmetric glass icon buttons (iteración 2b).
                ToolbarItem(placement: .topBarLeading) {
                    ChampionshipMenu(viewModel: viewModel)
                }
                ToolbarItem(placement: .topBarLeading) {
                    SortMenu(viewModel: viewModel)
                }
                ToolbarItem(placement: .primaryAction) {
                    settingsMenu
                }
            }
            .task { await viewModel.loadIfNeeded() }
            .onChange(of: viewModel.state) { _, newState in
                if case .error = newState { retryFocused = true }
            }
    }

    /// Settings / overflow menu (D5). Hosts the logout item, which runs the
    /// same F1 seam owned by `SplashView` (`AuthViewModel.logout()` +
    /// `phase = .noSession`); this view never touches session logic directly.
    /// Styled as a `DSGlassIcon` so it matches the leading trophy/sort buttons.
    private var settingsMenu: some View {
        Menu {
            Button(role: .destructive, action: onLogout) {
                Label("Cerrar sesión", systemImage: "rectangle.portrait.and.arrow.right")
            }
        } label: {
            DSGlassIcon(systemImage: "ellipsis")
        }
        .accessibilityLabel("Ajustes")
    }

    /// True while the screen is in its initial load (drives the crossfade).
    private var isLoadingState: Bool { viewModel.state == .loading }

    @ViewBuilder
    private var content: some View {
        switch viewModel.state {
        case .loading:
            // The CrossfadeLoader overlays the row skeleton while loading.
            Color.clear

        case .loaded(let teams):
            ScrollView {
                VStack(spacing: DSSpacingSwiftUI.md) {
                    ForEach(teams) { team in
                        teamLink(for: team)
                    }
                }
                .padding(DSSpacingSwiftUI.md)
            }
            .refreshable { await viewModel.load() }

        case .emptyTeams:
            messageView("Este campeonato no tiene equipos aún.")

        case .noChampionships:
            messageView("No tienes campeonatos.")

        case .error(let message):
            VStack(spacing: DSSpacingSwiftUI.md) {
                ErrorState(message: message)
                Button("Reintentar") {
                    Task { await viewModel.load() }
                }
                .buttonStyle(.bordered)
                .frame(minHeight: 44)
                .accessibilityLabel("Reintentar")
                .accessibilityFocused($retryFocused)
            }
            .padding(DSSpacingSwiftUI.lg)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    // MARK: - Navigation (FR6)

    /// A tappable budget card that pushes the team-detail screen. Uses a
    /// value-based `NavigationLink(value:)` so it works with the stack's
    /// `.navigationDestination(for:)`. On iOS 18+ the source card is tagged with
    /// `.matchedTransitionSource` so the push animates as a zoom from the card;
    /// older runtimes just push normally.
    private func teamLink(for team: TeamBudget) -> some View {
        let route = TeamDetailRoute(teamId: team.teamId, teamName: team.teamName)
        return NavigationLink(value: route) {
            BudgetRow(team: team)
        }
        .buttonStyle(.plain)
        .modifier(ZoomSource(id: team.teamId, namespace: zoomNamespace))
    }

    /// Builds the pushed detail screen for `route`, applying the iOS 18+ zoom
    /// navigation transition under the shared namespace when available.
    @ViewBuilder
    private func detailDestination(for route: TeamDetailRoute) -> some View {
        let detail = TeamDetailView(
            viewModel: makeTeamDetailViewModel(),
            route: route
        )
        if #available(iOS 18.0, macOS 15.0, *) {
            detail.navigationTransition(.zoom(sourceID: route.teamId, in: zoomNamespace))
        } else {
            detail
        }
    }

    private func messageView(_ text: String) -> some View {
        Text(text)
            .font(DSFont.body)
            .foregroundStyle(DSColor.onSurfaceVariant)
            .multilineTextAlignment(.center)
            .padding(DSSpacingSwiftUI.lg)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .accessibilityElement(children: .combine)
            .accessibilityLabel(text)
    }
}

/// Applies `.matchedTransitionSource(id:in:)` to the source card on iOS 18+ so
/// the push to the team detail animates as a zoom; a no-op on older runtimes
/// (the push then falls back to the default animation). Factored into a
/// modifier so the `#available` guard stays off the `ForEach` body.
@available(iOS 17.0, macOS 14.0, *)
private struct ZoomSource: ViewModifier {
    let id: String
    let namespace: Namespace.ID

    func body(content: Content) -> some View {
        if #available(iOS 18.0, macOS 15.0, *) {
            content.matchedTransitionSource(id: id, in: namespace)
        } else {
            content
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
