import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// The single sheet the market screen can present (W4 bid / W7 Sofascore
/// detail). One `.sheet(item:)` driven by this enum — attaching two separate
/// `.sheet` modifiers to the same view makes only the last one present, which
/// is why the Sofascore detail silently did nothing.
@available(iOS 17.0, macOS 14.0, *)
enum MarketSheetRoute: Identifiable {
    case bid(MarketPlayer)
    case sofascore(MarketPlayer)

    var id: String {
        switch self {
        case .bid(let p): return "bid-\(p.playerId)"
        case .sofascore(let p): return "sofascore-\(p.playerId)"
        }
    }
}

/// Market screen (V1 / US1–US7). Lives inside a `NavigationStack` provided by
/// `RootTabView` (2nd tab). Composes the economy banner, the sort control, the
/// player list, and the shared F1/F2 loading/error/empty states. Reuses the
/// DesignSystem tokens and components so it matches the Presupuesto tab.
///
/// The body switches on `MarketLoadState`:
/// - `.idle`/`.loading` → `SkeletonScreen` (skeleton de carga)
/// - `.data`            → banner + sort bar + `LazyVStack` of `MarketPlayerCard`
/// - `.empty`           → "No hay jugadores del computer disponibles."
/// - `.error`           → `ErrorState` + Reintentar
///
/// It reloads on appear and whenever the active championship id changes
/// (`onChange`). A write notice is surfaced via an alert.
@available(iOS 17.0, macOS 14.0, *)
public struct MarketView: View {
    @Bindable private var viewModel: MarketViewModel
    /// Shared budget view model — the SAME instance the Presupuesto tab uses —
    /// so the toolbar championship selector drives both tabs through the shared
    /// `ActiveChampionshipStore` (transversal control, like Presupuesto).
    @Bindable private var budgetViewModel: BudgetViewModel
    private let onLogout: () -> Void

    /// Sheet routing state, local to the screen.
    @State private var activeSheet: MarketSheetRoute?
    @State private var cancelTarget: MarketPlayer?
    /// Whether the compact economy pill is shown (banner scrolled off). A single
    /// Bool — flipped only when crossing the threshold — so scrolling does NOT
    /// re-evaluate the whole grid on every frame (keeps it smooth at 120 Hz).
    @State private var showCompactPill = false

    /// Factory for a fresh Sofascore detail view model per opened sheet (W7),
    /// so its state is isolated from the list (FR8.2).
    private let makeSofascoreViewModel: () -> SofascoreDetailViewModel

    @AccessibilityFocusState private var retryFocused: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.openURL) private var openURL

    /// Scroll distance (pt) past which the compact economy pill appears (the
    /// big banner has scrolled roughly off by then).
    private let collapseDistance: CGFloat = 90

    public init(
        viewModel: MarketViewModel,
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
            SkeletonScreen(showHeader: true)
        } content: {
            content
        }
            .authenticatedBackground()
            .navigationTitle("Mercado")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                // Transversal toolbar, symmetric with Presupuesto: trophy
                // championship selector + sort bubble (leading) — title —
                // settings/overflow ellipsis (trailing). All DSGlassIcon.
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
                Task { await viewModel.load() }
            }
            .onChange(of: viewModel.loadState) { _, newState in
                if case .error = newState { retryFocused = true }
            }
            .sheet(item: $activeSheet) { route in
                switch route {
                case .bid(let player):
                    bidSheet(for: player)
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
            .confirmationDialog(
                "¿Cancelar la puja activa?",
                isPresented: cancelDialogBinding,
                titleVisibility: .visible
            ) {
                Button("Cancelar puja", role: .destructive) {
                    if let player = cancelTarget {
                        Task { await viewModel.cancelBid(player: player) }
                    }
                    cancelTarget = nil
                }
                Button("No", role: .cancel) { cancelTarget = nil }
            }
            .alert(item: $viewModel.lastWriteNotice) { notice in
                Alert(title: Text(notice.message), dismissButton: .default(Text("Entendido")))
            }
            .overlay(alignment: .top) { floatingSummary }
    }

    /// Compact economy pill that appears, floating at the top, once the big
    /// banner has scrolled away — the exact essentials the old pill showed
    /// (Disponible · Presupuesto · Balance). A smooth fade + slide-down, not a
    /// resize of the banner. Hidden while the banner is still visible.
    @ViewBuilder
    private var floatingSummary: some View {
        if viewModel.loadState == .data, let info = viewModel.userInfo, showCompactPill {
            CompactEconomyPill(userInfo: info)
                .padding(.horizontal, DSSpacingSwiftUI.md)
                .padding(.top, DSSpacingSwiftUI.xs)
                .transition(
                    reduceMotion
                        ? .opacity
                        : .move(edge: .top).combined(with: .opacity)
                )
        }
    }

    /// Show the floating pill once scrolled past the banner (with a little
    /// hysteresis via the fixed threshold); animated by `scrollOffset` changes.
    // MARK: - Content by state

    /// True while the screen is in its initial load (drives the crossfade).
    private var isLoadingState: Bool {
        viewModel.loadState == .idle || viewModel.loadState == .loading
    }

    @ViewBuilder
    private var content: some View {
        switch viewModel.loadState {
        case .idle, .loading:
            // The CrossfadeLoader overlays the skeleton while loading.
            Color.clear

        case .data:
            ScrollView {
                VStack(spacing: DSSpacingSwiftUI.md) {
                    // The full economy banner lives in the scroll and scrolls
                    // away like any content; the compact pill takes over on top.
                    if let info = viewModel.userInfo {
                        MarketBanner(userInfo: info)
                    }
                    countLabel
                    LazyVGrid(
                        columns: [
                            GridItem(.flexible(), spacing: DSSpacingSwiftUI.md),
                            GridItem(.flexible(), spacing: DSSpacingSwiftUI.md)
                        ],
                        spacing: DSSpacingSwiftUI.md
                    ) {
                        ForEach(viewModel.players) { player in
                            MarketPlayerCard(
                                player: player,
                                isWriting: viewModel.isWriting,
                                onBid: { activeSheet = .bid(player) },
                                onCancel: { cancelTarget = player },
                                onOpenSofascore: { activeSheet = .sofascore(player) },
                                onOpenSofascoreProfile: { openSofascoreProfile(player) }
                            )
                            .modifier(CardEntrance(enabled: !reduceMotion))
                        }
                    }
                }
                .padding(.horizontal, DSSpacingSwiftUI.md)
                .padding(.bottom, DSSpacingSwiftUI.md)
            }
            .modifier(ScrollOffsetReader { newValue in
                let shouldShow = newValue > collapseDistance
                if shouldShow != showCompactPill {
                    withAnimation(reduceMotion ? nil : .spring(response: 0.38, dampingFraction: 0.82)) {
                        showCompactPill = shouldShow
                    }
                }
            })
            .refreshable { await viewModel.load() }

        case .empty:
            messageView("No hay jugadores del computer disponibles.")

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

    // MARK: - Toolbar affordances

    /// Sort selector rendered as a NATIVE `Menu` (same mechanic as the trophy
    /// championship selector), not a bottom sheet. Each field is a menu item;
    /// the active one carries a checkmark. Selecting re-sorts in memory (W3).
    private var sortMenu: some View {
        Menu {
            ForEach(MarketSortField.allCases, id: \.self) { field in
                Button {
                    viewModel.setSort(field)
                } label: {
                    if field == viewModel.sortField {
                        Label(field.displayLabel, systemImage: "checkmark")
                    } else {
                        Label(field.displayLabel, systemImage: field.symbolName)
                    }
                }
            }
        } label: {
            DSGlassIcon(systemImage: "arrow.up.arrow.down")
        }
        .accessibilityLabel("Ordenar por \(viewModel.sortField.displayLabel), abre opciones")
    }

    /// Settings / overflow menu (D5), symmetric with Presupuesto. Hosts the
    /// logout item, which runs the same F1 seam owned by `SplashView`; styled
    /// as a `DSGlassIcon` so it matches the leading trophy/sort buttons.
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

    /// "N jugadores disponibles" count line (Angular `.count`).
    private var countLabel: some View {
        HStack {
            Text("\(viewModel.players.count) jugadores disponibles")
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurfaceVariant)
            Spacer()
        }
        .accessibilityLabel("\(viewModel.players.count) jugadores disponibles")
    }

    // MARK: - Sheets

    /// Opens the player's Sofascore web profile in the system browser (recovers
    /// the Angular "tap the avatar → sofascore.com" behaviour). No-op if the
    /// player has no `sofascore_url`.
    private func openSofascoreProfile(_ player: MarketPlayer) {
        guard let urlString = player.sofascoreUrl,
              !urlString.isEmpty,
              let url = URL(string: urlString) else { return }
        openURL(url)
    }

    private func bidSheet(for player: MarketPlayer) -> some View {
        Group {
            if let info = viewModel.userInfo {
                BidSheet(player: player, userInfo: info) { price in
                    Task { await viewModel.placeBid(player: player, price: price) }
                    activeSheet = nil
                }
            } else {
                // Defensive: a bid cannot be composed without the banner data.
                Text("No se pudo abrir la puja.")
                    .font(DSFont.body)
                    .padding(DSSpacingSwiftUI.lg)
            }
        }
    }

    /// A `confirmationDialog` needs a `Bool` binding; derive it from the
    /// optional target so dismissing clears the target.
    private var cancelDialogBinding: Binding<Bool> {
        Binding(
            get: { cancelTarget != nil },
            set: { presented in if !presented { cancelTarget = nil } }
        )
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

/// Human labels for the sort fields (Spanish UI strings). Kept as a view-layer
/// extension so `FutmondoKit` stays free of presentation text.
@available(iOS 17.0, macOS 14.0, *)
extension MarketSortField {
    var displayLabel: String {
        switch self {
        case .value: return "Valor"
        case .change: return "Tendencia"
        case .sofascoreRating: return "Rating Sofascore"
        case .starterPct: return "% Titular"
        case .suggestedBid: return "Puja sugerida"
        case .points: return "Puntos"
        case .average: return "Media"
        }
    }

    var symbolName: String {
        switch self {
        case .value: return "eurosign.circle"
        case .change: return "chart.line.uptrend.xyaxis"
        case .sofascoreRating: return "star.circle"
        case .starterPct: return "person.fill.checkmark"
        case .suggestedBid: return "hand.raised.circle"
        case .points: return "number.circle"
        case .average: return "chart.bar"
        }
    }
}

/// Native scroll-driven entrance for each market card (iOS 17+): cards fade and
/// scale in as they reach the viewport (`scrollTransition`), giving the list a
/// lively, staggered feel without any manual timers. A no-op when Reduce Motion
/// is on or on older runtimes, so the content never hides.
@available(iOS 17.0, macOS 14.0, *)
private struct CardEntrance: ViewModifier {
    let enabled: Bool

    func body(content: Content) -> some View {
        if enabled, #available(iOS 17.0, *) {
            content.scrollTransition { view, phase in
                view
                    .opacity(phase.isIdentity ? 1 : 0)
                    .scaleEffect(phase.isIdentity ? 1 : 0.92)
                    .offset(y: phase.isIdentity ? 0 : 16)
            }
        } else {
            content
        }
    }
}

/// Reports the vertical scroll offset (pt, >= 0) of the enclosing ScrollView.
/// Uses the native `onScrollGeometryChange` on iOS 18+ (the app ships iOS 26),
/// which is the reliable way to observe scrolling; a GeometryReader+preference
/// fallback covers older runtimes.
@available(iOS 17.0, macOS 14.0, *)
private struct ScrollOffsetReader: ViewModifier {
    let onChange: (CGFloat) -> Void

    func body(content: Content) -> some View {
        if #available(iOS 18.0, macOS 15.0, *) {
            content.onScrollGeometryChange(for: CGFloat.self) { geo in
                geo.contentOffset.y + geo.contentInsets.top
            } action: { _, newValue in
                onChange(max(0, newValue))
            }
        } else {
            content
                .coordinateSpace(.named("marketScroll"))
                .overlay(alignment: .top) {
                    GeometryReader { _ in Color.clear }
                        .frame(height: 0)
                }
                .background(
                    GeometryReader { geo in
                        Color.clear.preference(
                            key: LegacyScrollOffsetKey.self,
                            value: -geo.frame(in: .named("marketScroll")).minY
                        )
                    }
                )
                .onPreferenceChange(LegacyScrollOffsetKey.self) { onChange(max(0, $0)) }
        }
    }
}

/// Legacy preference key for the pre-iOS-18 scroll-offset fallback.
@available(iOS 17.0, macOS 14.0, *)
private struct LegacyScrollOffsetKey: PreferenceKey {
    static let defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

/// Compact economy pill shown floating at the top once the banner scrolls away
/// — the exact essentials the old pill showed: **Disponible** (the money you
/// can commit) leading, then Presupuesto and Balance. The noise (En pujas
/// count) is dropped. A glass capsule; money colour is paired with a label so
/// meaning is never colour-only (A7).
@available(iOS 17.0, macOS 14.0, *)
private struct CompactEconomyPill: View {
    let userInfo: MarketUserInfo

    private var availableHealthy: Bool { userInfo.availableForBids > 0 }

    var body: some View {
        HStack(spacing: DSSpacingSwiftUI.md) {
            figure(
                "DISPONIBLE",
                money(userInfo.availableForBids),
                color: availableHealthy ? DSColor.moneyPositive : DSColor.moneyNegative,
                alignment: .leading,
                hero: true
            )
            Divider().frame(height: 24).overlay(DSColor.onSurface.opacity(0.2))
            figure("PRESUPUESTO", money(userInfo.balance), color: DSColor.onSurface, alignment: .leading)
            figure(
                "BALANCE",
                MoneyFormatter.format(userInfo.balanceMinusBids, signed: true),
                color: userInfo.balanceMinusBids >= 0 ? DSColor.moneyPositive : DSColor.moneyNegative,
                alignment: .trailing
            )
        }
        .padding(.horizontal, DSSpacingSwiftUI.md)
        .padding(.vertical, DSSpacingSwiftUI.sm)
        .background(.ultraThinMaterial, in: Capsule())
        .background(Color.black.opacity(0.35), in: Capsule())
        .overlay(Capsule().stroke(DSColor.primary.opacity(0.35), lineWidth: 1))
        .shadow(color: .black.opacity(0.35), radius: 10, y: 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            "Disponible \(money(userInfo.availableForBids)), "
            + "presupuesto \(money(userInfo.balance)), "
            + "balance \(MoneyFormatter.format(userInfo.balanceMinusBids, signed: true))"
        )
    }

    private func figure(_ label: String, _ value: String, color: Color, alignment: HorizontalAlignment, hero: Bool = false) -> some View {
        VStack(alignment: alignment, spacing: 0) {
            Text(label)
                .font(.system(size: 8, weight: .heavy))
                .foregroundStyle(DSColor.onSurfaceVariant)
                .lineLimit(1)
                .fixedSize()
            Text(value)
                .font(hero ? .subheadline.weight(.heavy) : .caption.weight(.semibold))
                .foregroundStyle(color)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
        }
        .frame(maxWidth: .infinity, alignment: alignment == .trailing ? .trailing : .leading)
    }

    private func money(_ amount: Int) -> String { MoneyFormatter.format(amount, signed: false) }
}

#endif // canImport(SwiftUI) && canImport(Observation)
