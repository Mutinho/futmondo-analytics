import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// The single sheet the favourites screen can present (W5 remove-confirm / W5
/// Sofascore detail). One `.sheet(item:)` driven by this enum — attaching two
/// separate `.sheet` modifiers to the same view makes only the last one present
/// (native-ios-ui-patterns.md), so both routes go through one modifier.
@available(iOS 17.0, macOS 14.0, *)
enum FavoritesSheetRoute: Identifiable {
    case confirmRemove(FavoritePlayer)
    case sofascore(FavoritePlayer)

    var id: String {
        switch self {
        case .confirmRemove(let p): return "remove-\(p.playerId)"
        case .sofascore(let p): return "sofascore-\(p.playerId)"
        }
    }
}

/// Favoritos screen (V1 / FR1–FR8). Lives inside a `NavigationStack` provided
/// by `RootTabView` (4th tab). Composes the toolbar (championship selector +
/// sort menu + settings), the count line, the shared loading/error/empty
/// states, and a `LazyVGrid` of `FavoritePlayerCard`. Reuses the DesignSystem
/// tokens and components so it matches the Mercado/Presupuesto tabs.
///
/// The body switches on `FavoritesLoadState`:
/// - `.idle`/`.loading` → `SkeletonScreen` (skeleton de carga)
/// - `.data`            → count line + `LazyVGrid` of `FavoritePlayerCard`
/// - `.empty`           → star icon + "No tienes jugadores favoritos libres…"
/// - `.error`           → `ErrorState` + Reintentar
///
/// It reloads on appear (`loadIfNeeded`) and whenever the active championship
/// id changes (`onChange` of the @Observable `BudgetViewModel.activeChampionship`
/// — BR1.2), plus pull-to-refresh (`.refreshable`).
@available(iOS 17.0, macOS 14.0, *)
public struct FavoritesView: View {
    @Bindable private var viewModel: FavoritesViewModel
    /// Shared budget view model — the SAME instance the other tabs use — so the
    /// toolbar championship selector drives every tab through the shared
    /// `ActiveChampionshipStore` (transversal control).
    @Bindable private var budgetViewModel: BudgetViewModel
    private let onLogout: () -> Void

    @State private var activeSheet: FavoritesSheetRoute?

    /// Factory for a fresh Sofascore detail view model per opened sheet (W5),
    /// so its state is isolated from the list.
    private let makeSofascoreViewModel: () -> SofascoreDetailViewModel

    @AccessibilityFocusState private var retryFocused: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.openURL) private var openURL

    public init(
        viewModel: FavoritesViewModel,
        budgetViewModel: BudgetViewModel,
        onLogout: @escaping () -> Void,
        makeSofascoreViewModel: @escaping () -> SofascoreDetailViewModel
    ) {
        self.viewModel = viewModel
        self.budgetViewModel = budgetViewModel
        self.onLogout = onLogout
        self.makeSofascoreViewModel = makeSofascoreViewModel
    }

    public var body: some View {
        CrossfadeLoader(isLoading: isLoadingState) {
            SkeletonScreen(showHeader: false)
        } content: {
            content
        }
            .authenticatedBackground()
            .navigationTitle("Favoritos")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    ChampionshipMenu(viewModel: budgetViewModel)
                }
                ToolbarItem(placement: .topBarLeading) {
                    sortMenu
                }
                ToolbarItem(placement: .primaryAction) {
                    settingsMenu
                }
            }
            .task { await viewModel.loadIfNeeded() }
            .onChange(of: budgetViewModel.activeChampionship?.championshipId) { _, _ in
                // Observe the @Observable BudgetViewModel.activeChampionship —
                // the property the shared selector mutates — not the plain
                // activeStore.activeId getter (which SwiftUI does not track).
                // (BR1.2 — avoids the Mercado/Calculadora reload bug.)
                Task { await viewModel.load() }
            }
            .onChange(of: viewModel.loadState) { _, newState in
                if case .error = newState { retryFocused = true }
            }
            .sheet(item: $activeSheet) { route in
                switch route {
                case .confirmRemove(let player):
                    ConfirmSheet(
                        icon: "star.slash.fill",
                        title: "Quitar de favoritos",
                        message: "¿Quitar a \(player.name) de tus favoritos?",
                        confirmLabel: "Quitar",
                        confirmRole: .destructive
                    ) {
                        Task {
                            // Local optimistic removal + animated reflow of the
                            // remaining cards (BR5.2); no refetch. Reduce Motion
                            // disables the animation.
                            await viewModel.unfollow(player: player)
                        }
                    }
                case .sofascore(let player):
                    SofascoreDetailSheet(
                        playerName: player.name,
                        sofascoreURL: player.sofascoreUrl,
                        teamLogo: player.teamLogo,
                        playerSlug: player.slug,
                        viewModel: makeSofascoreViewModel()
                    )
                }
            }
            .alert(item: $viewModel.lastNotice) { notice in
                Alert(title: Text(notice.message), dismissButton: .default(Text("Entendido")))
            }
    }

    // MARK: - Content by state

    /// True while the screen is in its initial load (drives the crossfade).
    private var isLoadingState: Bool {
        viewModel.loadState == .idle || viewModel.loadState == .loading
    }

    @ViewBuilder
    private var content: some View {
        switch viewModel.loadState {
        case .idle, .loading:
            // The CrossfadeLoader overlays the skeleton while loading; the
            // content layer is just a clear placeholder underneath.
            Color.clear

        case .data:
            ScrollView {
                VStack(spacing: DSSpacingSwiftUI.md) {
                    countLabel
                    LazyVGrid(
                        columns: [
                            GridItem(.flexible(), spacing: DSSpacingSwiftUI.md),
                            GridItem(.flexible(), spacing: DSSpacingSwiftUI.md)
                        ],
                        spacing: DSSpacingSwiftUI.md
                    ) {
                        ForEach(viewModel.players) { player in
                            FavoritePlayerCard(
                                player: player,
                                isWriting: viewModel.isWriting,
                                onRemove: { activeSheet = .confirmRemove(player) },
                                onOpenSofascore: { activeSheet = .sofascore(player) },
                                onOpenSofascoreProfile: { openSofascoreProfile(player) }
                            )
                            .transition(reduceMotion ? .opacity : .scale.combined(with: .opacity))
                        }
                    }
                    // Smooth reflow of the remaining cards when one is removed
                    // (BR5.2). Keyed to the id list so an optimistic local
                    // removal animates; no-op under Reduce Motion.
                    .animation(
                        reduceMotion ? nil : .spring(response: 0.38, dampingFraction: 0.82),
                        value: viewModel.players.map(\.playerId)
                    )
                }
                .padding(.horizontal, DSSpacingSwiftUI.md)
                .padding(.bottom, DSSpacingSwiftUI.md)
            }
            .refreshable { await viewModel.load() }

        case .empty:
            emptyState

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

    // MARK: - Empty state (BR2.1)

    private var emptyState: some View {
        VStack(spacing: DSSpacingSwiftUI.sm) {
            Image(systemName: "star")
                .font(.system(size: 44))
                .foregroundStyle(DSColor.onSurfaceVariant)
                .accessibilityHidden(true)
            Text("No tienes jugadores favoritos libres")
                .font(DSFont.h3)
                .foregroundStyle(DSColor.onSurface)
                .multilineTextAlignment(.center)
            Text("Marca jugadores como favoritos desde el mercado para verlos aquí.")
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurfaceVariant)
                .multilineTextAlignment(.center)
        }
        .padding(DSSpacingSwiftUI.lg)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("No tienes jugadores favoritos libres. Marca jugadores como favoritos desde el mercado para verlos aquí.")
    }

    // MARK: - Toolbar affordances

    /// Sort selector rendered as a NATIVE `Menu` (same mechanic as the trophy
    /// championship selector). Each field is a `Toggle` row so the labels stay
    /// aligned (native-ios-ui-patterns.md); selecting re-sorts in memory and
    /// persists the choice (W3 / BR4.1).
    private var sortMenu: some View {
        Menu {
            ForEach(FavoritesSortField.allCases, id: \.self) { field in
                Toggle(
                    isOn: Binding(
                        get: { field == viewModel.sortField },
                        set: { selected in if selected { viewModel.setSort(field) } }
                    )
                ) {
                    Label(field.displayLabel, systemImage: field.symbolName)
                }
            }
        } label: {
            DSGlassIcon(systemImage: "arrow.up.arrow.down")
        }
        .accessibilityLabel("Ordenar por \(viewModel.sortField.displayLabel), abre opciones")
    }

    /// Settings / overflow menu, symmetric with the other tabs. Hosts logout.
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

    /// "N jugadores favoritos libres" count line (BR3.4).
    private var countLabel: some View {
        HStack {
            Text("\(viewModel.players.count) jugadores favoritos libres")
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurfaceVariant)
            Spacer()
        }
        .accessibilityLabel("\(viewModel.players.count) jugadores favoritos libres")
    }

    // MARK: - Sofascore external profile

    /// Opens the player's Sofascore web profile in the system browser (W5 /
    /// BR6.1). No-op if the player has no `sofascore_url`.
    private func openSofascoreProfile(_ player: FavoritePlayer) {
        guard let urlString = player.sofascoreUrl,
              !urlString.isEmpty,
              let url = URL(string: urlString) else { return }
        openURL(url)
    }
}

/// Human labels + SF Symbols for the favourites sort fields (Spanish UI
/// strings). Kept as a view-layer extension so `FutmondoKit` stays free of
/// presentation text.
@available(iOS 17.0, macOS 14.0, *)
extension FavoritesSortField {
    var displayLabel: String {
        switch self {
        case .value: return "Valor"
        case .change: return "Tendencia"
        case .sofascoreRating: return "Rating Sofascore"
        case .starterPct: return "% Titular"
        case .points: return "Puntos"
        }
    }

    var symbolName: String {
        switch self {
        case .value: return "eurosign.circle"
        case .change: return "chart.line.uptrend.xyaxis"
        case .sofascoreRating: return "star.circle"
        case .starterPct: return "person.fill.checkmark"
        case .points: return "number.circle"
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
