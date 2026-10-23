import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

/// The confirmation the Calculadora can present (sell the selection, or cancel
/// one on-sale player), routed through a single `.sheet(item:)`.
@available(iOS 17.0, macOS 14.0, *)
enum CalculatorConfirmRoute: Identifiable {
    case sell
    case cancel(OnSalePlayer)

    var id: String {
        switch self {
        case .sell: return "sell"
        case .cancel(let p): return "cancel-\(p.playerId)"
        }
    }
}

/// Calculadora screen (FR2–FR10). Lives inside a `NavigationStack` provided by
/// `RootTabView` (3rd tab). Composes the economy header (with the on-sale
/// toggle), the native date projection, the sort `Menu`, the on-sale section,
/// the selectable player grid (Mercado tile aesthetic), and the floating
/// "Vender (N)" CTA. Reuses the DesignSystem tokens and the shared
/// `DataFreshness`/`loadIfNeeded`/`.refreshable` caching pattern so switching
/// tabs does not refetch (BR11.1).
///
/// The body switches on `CalculatorLoadState`:
/// - `.idle`/`.loading` → `SkeletonScreen` (skeleton de carga)
/// - `.data`            → header + date + sort + on-sale + grid
/// - `.empty`           → "No hay jugadores en tu plantilla."
/// - `.error`           → `ErrorState` + Reintentar
@available(iOS 17.0, macOS 14.0, *)
public struct CalculatorView: View {
    @Bindable private var viewModel: CalculatorViewModel
    /// Shared budget view model — the SAME instance the other tabs use — so the
    /// toolbar championship selector drives every tab through the shared
    /// `ActiveChampionshipStore`.
    @Bindable private var budgetViewModel: BudgetViewModel
    private let onLogout: () -> Void

    /// The chosen projection date (W3). Bound to the native `DatePicker`; its
    /// whole-day delta from today drives `daysAhead` (BR1.2).
    @State private var projectionDate: Date = Date()
    /// Whether the floating date popover is open (date is now a toolbar button
    /// to the right of sort, not an in-scroll card).
    @State private var showingDatePopover = false
    /// Whether the compact summary pill is shown (header scrolled off). A single
    /// Bool — flipped only at the threshold — so scrolling does not re-evaluate
    /// the whole grid every frame (smooth at 120 Hz), mirroring Mercado.
    @State private var showCompactPill = false
    /// The confirmation sheet currently presented (sell or cancel), routed via
    /// a single `.sheet(item:)` (two separate `.sheet` would clash).
    @State private var activeConfirm: CalculatorConfirmRoute?

    @AccessibilityFocusState private var retryFocused: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    /// Scroll distance (pt) past which the compact summary pill appears (the
    /// economy header has scrolled roughly off by then).
    private let collapseDistance: CGFloat = 120

    public init(
        viewModel: CalculatorViewModel,
        budgetViewModel: BudgetViewModel,
        onLogout: @escaping () -> Void
    ) {
        self.viewModel = viewModel
        self.budgetViewModel = budgetViewModel
        self.onLogout = onLogout
    }

    public var body: some View {
        CrossfadeLoader(isLoading: isLoadingState) {
            SkeletonScreen(showHeader: true)
        } content: {
            content
        }
            .authenticatedBackground()
            .navigationTitle("Calculadora")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    ChampionshipMenu(viewModel: budgetViewModel)
                }
                ToolbarItem(placement: .topBarLeading) {
                    sortMenu
                }
                ToolbarItem(placement: .topBarLeading) {
                    dateButton
                }
                ToolbarItem(placement: .primaryAction) {
                    settingsMenu
                }
            }
            .task { await viewModel.loadIfNeeded() }
            .onChange(of: budgetViewModel.activeChampionship?.championshipId) { _, _ in
                // Observe the @Observable BudgetViewModel.activeChampionship —
                // the property the shared selector actually mutates. The old
                // onChange watched activeStore.activeId (a plain UserDefaults
                // getter) which SwiftUI does not track, so switching the
                // championship never reloaded the Calculadora (FR1.3).
                Task { await viewModel.load() }
            }
            .onChange(of: viewModel.loadState) { _, newState in
                if case .error = newState { retryFocused = true }
            }
            .sheet(item: $activeConfirm) { route in
                switch route {
                case .sell:
                    ConfirmSheet(
                        icon: "tag.fill",
                        title: "Poner a la venta",
                        message: "¿Poner a la venta \(viewModel.selectedCount) jugador(es) a su valor de mercado actual?",
                        confirmLabel: "Poner a la venta",
                        confirmRole: nil,
                        onConfirm: { Task { await viewModel.sellSelected() } }
                    )
                case .cancel(let player):
                    ConfirmSheet(
                        icon: "xmark.circle.fill",
                        title: "Retirar del mercado",
                        message: "¿Retirar a \(player.name) del mercado?",
                        confirmLabel: "Retirar del mercado",
                        confirmRole: .destructive,
                        onConfirm: { Task { await viewModel.cancelSale(playerId: player.playerId) } }
                    )
                }
            }
            .alert(item: $viewModel.lastNotice) { notice in
                Alert(title: Text(notice.message), dismissButton: .default(Text("Entendido")))
            }
            .overlay(alignment: .top) { floatingSummary }
            .overlay(alignment: .bottomTrailing) { floatingSell }
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
            // The CrossfadeLoader overlays the skeleton while loading.
            Color.clear

        case .data:
            ScrollView {
                VStack(spacing: DSSpacingSwiftUI.md) {
                    header
                    // On-sale cards section only when toggle ON + non-empty
                    // (BR6.1); the header figure stays regardless.
                    if viewModel.includeOnSale && !viewModel.onSalePlayers.isEmpty {
                        OnSaleSection(
                            players: viewModel.onSalePlayers,
                            isWriting: viewModel.isWriting,
                            onCancel: { activeConfirm = .cancel($0) }
                        )
                    }
                    countLabel
                    grid
                }
                .padding(.horizontal, DSSpacingSwiftUI.md)
                .padding(.bottom, 96) // room for the floating CTA
            }
            .modifier(CalcScrollOffsetReader { newValue in
                let shouldShow = newValue > collapseDistance
                if shouldShow != showCompactPill {
                    withAnimation(reduceMotion ? nil : .spring(response: 0.38, dampingFraction: 0.82)) {
                        showCompactPill = shouldShow
                    }
                }
            })
            .refreshable { await viewModel.load() }

        case .empty:
            messageView("No hay jugadores en tu plantilla.")

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

    private var header: some View {
        CalculatorHeader(
            balance: viewModel.economy?.balance ?? 0,
            onSaleTotal: viewModel.onSaleTotal,
            activeBidsTotal: viewModel.economy?.activeBidsTotal ?? 0,
            activeBidsCount: viewModel.economy?.activeBidsCount ?? 0,
            selectedTotal: viewModel.selectedTotal,
            futureBalance: viewModel.futureBalance,
            includeOnSale: viewModel.includeOnSale,
            onToggleIncludeOnSale: { viewModel.setIncludeOnSale($0) }
        )
    }

    // MARK: - Projection date (W3 / FR4) — floating toolbar button + popover

    /// Calendar icon button to the RIGHT of the sort button; opens a popover
    /// with the graphical `DatePicker`. Replaces the in-scroll date card so the
    /// list breathes. The chosen date's whole-day delta drives `daysAhead`.
    private var dateButton: some View {
        Button {
            showingDatePopover = true
        } label: {
            DSGlassIcon(systemImage: viewModel.daysAhead > 0 ? "calendar.badge.clock" : "calendar")
        }
        .popover(isPresented: $showingDatePopover) {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.md) {
                Text("Fecha de venta")
                    .font(DSFont.h3)
                    .foregroundStyle(DSColor.onSurface)
                DatePicker(
                    "Fecha de venta",
                    selection: $projectionDate,
                    in: Date()..., // today or later (FR4.1)
                    displayedComponents: .date
                )
                .labelsHidden()
                .datePickerStyle(.graphical)
                .tint(DSColor.primary)
                .onChange(of: projectionDate) { _, newValue in
                    viewModel.setDaysAhead(Self.wholeDaysFromToday(to: newValue))
                }
                Text(projectionLabel)
                    .font(.caption)
                    .foregroundStyle(DSColor.onSurfaceVariant)
                if viewModel.daysAhead > 0 {
                    Button("Hoy (quitar proyección)") {
                        projectionDate = Date()
                        viewModel.setDaysAhead(0)
                    }
                    .font(.caption.weight(.semibold))
                    .tint(DSColor.primary)
                }
            }
            .padding(DSSpacingSwiftUI.lg)
            .frame(minWidth: 320)
            .presentationCompactAdaptation(.popover)
        }
        .accessibilityLabel("Fecha de venta, \(projectionLabel)")
    }

    /// "Hoy (valor actual)" at day 0, or "N día/días a futuro" (FR4.4).
    private var projectionLabel: String {
        let days = viewModel.daysAhead
        if days == 0 { return "Hoy (valor actual)" }
        return days == 1 ? "1 día a futuro" : "\(days) días a futuro"
    }

    /// Whole days from today (00:00) to `date` (00:00), clamped to >= 0 (BR1.2).
    static func wholeDaysFromToday(to date: Date) -> Int {
        let calendar = Calendar.current
        let today = calendar.startOfDay(for: Date())
        let target = calendar.startOfDay(for: date)
        let days = calendar.dateComponents([.day], from: today, to: target).day ?? 0
        return max(0, days)
    }

    /// Light selection haptic when a player is (de)selected for sale. Native
    /// `UISelectionFeedbackGenerator`; a no-op off-device (no UIKit) and when
    /// Reduce Motion is on (haptics are part of motion/feedback the person
    /// chose to reduce).
    static func fireSelectionHaptic(reduceMotion: Bool) {
        guard !reduceMotion else { return }
        #if canImport(UIKit)
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
        #endif
    }

    // MARK: - Grid

    private var grid: some View {
        LazyVGrid(
            columns: [
                GridItem(.flexible(), spacing: DSSpacingSwiftUI.md),
                GridItem(.flexible(), spacing: DSSpacingSwiftUI.md)
            ],
            spacing: DSSpacingSwiftUI.md
        ) {
            ForEach(viewModel.players) { player in
                CalculatorPlayerCard(
                    player: player,
                    projectedValue: viewModel.projectedValue(for: player),
                    daysAhead: viewModel.daysAhead,
                    isSelected: viewModel.selectedIds.contains(player.playerId),
                    onTap: {
                        Self.fireSelectionHaptic(reduceMotion: reduceMotion)
                        viewModel.toggleSelection(player.playerId)
                    }
                )
            }
        }
    }

    private var countLabel: some View {
        HStack {
            Text("\(viewModel.players.count) jugadores disponibles")
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurfaceVariant)
            Spacer()
        }
        .accessibilityLabel("\(viewModel.players.count) jugadores disponibles")
    }

    // MARK: - Floating summary pill (appears on scroll, like Mercado)

    /// Compact summary pill that appears, floating at the top, once the economy
    /// header has scrolled away — the essentials: Saldo futuro · Seleccionadas ·
    /// Saldo actual. A smooth fade + slide-down, mirroring Mercado's pill.
    @ViewBuilder
    private var floatingSummary: some View {
        if viewModel.loadState == .data, showCompactPill {
            CalcSummaryPill(
                futureBalance: viewModel.futureBalance,
                selectedTotal: viewModel.selectedTotal,
                balance: viewModel.economy?.balance ?? 0
            )
            .padding(.horizontal, DSSpacingSwiftUI.md)
            .padding(.top, DSSpacingSwiftUI.xs)
            .transition(reduceMotion ? .opacity : .move(edge: .top).combined(with: .opacity))
        }
    }

    // MARK: - Floating sell CTA (FR8.1) — subtle glass pill, bottom-trailing

    @ViewBuilder
    private var floatingSell: some View {
        if viewModel.loadState == .data && viewModel.selectedCount > 0 {
            SellFloatingButton(
                count: viewModel.selectedCount,
                isWriting: viewModel.isWriting,
                action: { activeConfirm = .sell }
            )
            .padding(.trailing, DSSpacingSwiftUI.md)
            .padding(.bottom, DSSpacingSwiftUI.md)
            .transition(reduceMotion ? .opacity : .move(edge: .trailing).combined(with: .opacity))
        }
    }

    // MARK: - Toolbar affordances

    private var sortMenu: some View {
        Menu {
            ForEach(CalculatorSortField.allCases, id: \.self) { field in
                // A `Toggle` per row keeps the names aligned (the transversal
                // selector pattern): SwiftUI reserves the check gutter on every
                // row, so selected and unselected labels start at the same x.
                Toggle(isOn: Binding(
                    get: { field == viewModel.sortField },
                    set: { selected in if selected { viewModel.setSort(field) } }
                )) {
                    Text(field.displayLabel)
                }
            }
        } label: {
            DSGlassIcon(systemImage: "arrow.up.arrow.down")
        }
        .accessibilityLabel("Ordenar por \(viewModel.sortField.displayLabel), abre opciones")
    }

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

    // MARK: - Helpers

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

/// Human labels for the Calculadora sort fields (Spanish UI strings). A
/// view-layer extension so `FutmondoKit` stays free of presentation text.
@available(iOS 17.0, macOS 14.0, *)
extension CalculatorSortField {
    var displayLabel: String {
        switch self {
        case .projectedValue: return "Valor proyectado"
        case .value: return "Valor actual"
        case .change: return "Tendencia"
        case .profit: return "Plusvalía"
        }
    }
}

/// Reports the vertical scroll offset (pt, >= 0) of the enclosing ScrollView,
/// driving the floating summary pill. Native `onScrollGeometryChange` on
/// iOS 18+ (the app ships iOS 26); GeometryReader+preference fallback below.
/// Mirrors Mercado's `ScrollOffsetReader`.
@available(iOS 17.0, macOS 14.0, *)
private struct CalcScrollOffsetReader: ViewModifier {
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
                .coordinateSpace(.named("calcScroll"))
                .background(
                    GeometryReader { geo in
                        Color.clear.preference(
                            key: CalcLegacyScrollOffsetKey.self,
                            value: -geo.frame(in: .named("calcScroll")).minY
                        )
                    }
                )
                .onPreferenceChange(CalcLegacyScrollOffsetKey.self) { onChange(max(0, $0)) }
        }
    }
}

/// Legacy preference key for the pre-iOS-18 scroll-offset fallback.
@available(iOS 17.0, macOS 14.0, *)
private struct CalcLegacyScrollOffsetKey: PreferenceKey {
    static let defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

/// Compact summary pill shown floating at the top once the economy header
/// scrolls away — Saldo futuro (hero) · Seleccionadas · Saldo actual. A glass
/// capsule with a neon hairline, mirroring Mercado's `CompactEconomyPill`.
/// Money colour is paired with a label so meaning is never colour-only (NFR6).
@available(iOS 17.0, macOS 14.0, *)
private struct CalcSummaryPill: View {
    let futureBalance: Int
    let selectedTotal: Int
    let balance: Int

    var body: some View {
        HStack(spacing: DSSpacingSwiftUI.md) {
            figure(
                "SALDO FUTURO",
                MoneyFormatter.format(futureBalance, signed: true),
                color: futureBalance >= 0 ? DSColor.moneyPositive : DSColor.moneyNegative,
                alignment: .leading,
                hero: true
            )
            Divider().frame(height: 24).overlay(DSColor.onSurface.opacity(0.2))
            figure("SELECCIONADAS", money(selectedTotal), color: DSColor.primary, alignment: .leading)
            figure(
                "SALDO ACTUAL",
                money(balance),
                color: balance >= 0 ? DSColor.onSurface : DSColor.moneyNegative,
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
            "Saldo futuro \(MoneyFormatter.format(futureBalance, signed: true)), "
            + "seleccionadas \(money(selectedTotal)), "
            + "saldo actual \(money(balance))"
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
