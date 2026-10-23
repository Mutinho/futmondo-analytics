import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

#if canImport(UIKit)
import UIKit
#endif

/// Value-based navigation route to a team's detail screen (FR6). Carries the
/// team id and name so the destination can show the name immediately (the hero
/// title) while the detail loads. `Hashable` so it keys a value-based
/// `NavigationLink` / `.navigationDestination(for:)`.
public struct TeamDetailRoute: Hashable {
    public let teamId: String
    public let teamName: String

    public init(teamId: String, teamName: String) {
        self.teamId = teamId
        self.teamName = teamName
    }
}

/// Which transaction list the toolbar section menu is showing.
private enum TransactionSection: Hashable {
    case purchases
    case sales
}

/// Team-detail screen (FR6): a collapsing hero title, a summary of three glass
/// mini-cards, and the per-section purchases/sales list, with
/// empty/loading/error states. The Compras|Ventas selector is a toolbar glass
/// `Menu` button (iteración 2e) rather than an inline segmented control, so it
/// stays always-visible and matches the budget screen's white glass icons. The
/// loaded content fades + slides in gently after the zoom, with the transaction
/// rows staggered by index (a soft landing). Pushed onto the budget
/// `NavigationStack` when a `BudgetRow` is tapped; it shares the authenticated
/// dark background with the list so the zoom transition reads continuously.
@available(iOS 17.0, macOS 14.0, *)
public struct TeamDetailView: View {
    @Bindable private var viewModel: TeamDetailViewModel
    private let route: TeamDetailRoute

    @State private var section: TransactionSection = .purchases
    /// Drives the staggered entrance of the loaded content (iteración 2e). Set
    /// true once the detail reaches `.loaded`; a change animates the hero
    /// title, the summary cards and the transaction rows into place.
    @State private var hasAppeared = false
    /// VoiceOver focus so an error moves focus to the Reintentar button (NFR5).
    @AccessibilityFocusState private var retryFocused: Bool
    /// Honour the system Reduce Motion setting (NFR5 / A-accessibility): when
    /// on, the entrance skips the movement and content simply appears.
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(viewModel: TeamDetailViewModel, route: TeamDetailRoute) {
        self.viewModel = viewModel
        self.route = route
    }

    public var body: some View {
        content
            .authenticatedBackground()
            .navigationTitle(route.teamName)
            .navigationBarTitleDisplayMode(.large)
            .toolbar { sectionToolbar }
            .task { await viewModel.load(teamId: route.teamId) }
            .onChange(of: viewModel.state) { _, newState in
                switch newState {
                case .error:
                    retryFocused = true
                case .loaded:
                    // Soft landing after the zoom: flip the flag so the loaded
                    // content fades + slides in. Skip the movement under Reduce
                    // Motion (the flag flips without animation).
                    if reduceMotion {
                        hasAppeared = true
                    } else {
                        withAnimation(.easeOut(duration: 0.45)) { hasAppeared = true }
                    }
                case .loading:
                    hasAppeared = false
                }
            }
    }

    // MARK: - Toolbar (iteración 2e)

    /// The Compras|Ventas selector lives in the navigation bar as an
    /// always-visible GLASS `Menu` button (Opción A), matching the white glass
    /// icon buttons of the budget screen (trophy/sort/ellipsis). It is only
    /// present once the detail is `.loaded`, since its item labels carry the
    /// per-section counts. Selecting an item updates the existing `@State
    /// section`; the scroll body renders the chosen section's list.
    @ToolbarContentBuilder
    private var sectionToolbar: some ToolbarContent {
        if case .loaded(let detail) = viewModel.state {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    sectionButton(
                        "Compras (\(detail.purchases.count))",
                        for: .purchases
                    )
                    sectionButton(
                        "Ventas (\(detail.sales.count))",
                        for: .sales
                    )
                } label: {
                    DSGlassIcon(systemImage: "arrow.left.arrow.right")
                }
                .accessibilityLabel("Sección de operaciones, abre selector")
            }
        }
    }

    /// One row of the section menu, rendered as a native single-select
    /// `Toggle` so SwiftUI reserves the SAME leading checkmark gutter on every
    /// row and the titles all start at the same x (a plain Text/Label mix left
    /// the unticked row shifted) — the same alignment fix used by the
    /// championship selector. Selecting it updates `section` (the list swap
    /// animates and fires the guarded haptic via `.onChange`).
    @ViewBuilder
    private func sectionButton(_ title: String, for target: TransactionSection) -> some View {
        Toggle(
            isOn: Binding(
                get: { section == target },
                set: { selected in if selected { section = target } }
            )
        ) {
            Text(title)
        }
    }

    @ViewBuilder
    private var content: some View {
        switch viewModel.state {
        case .loading:
            LoadingState(message: "Cargando detalle")
                .frame(maxWidth: .infinity, maxHeight: .infinity)

        case .loaded(let detail):
            loadedContent(detail)

        case .error(let message):
            VStack(spacing: DSSpacingSwiftUI.md) {
                ErrorState(message: message)
                Button("Reintentar") {
                    Task { await viewModel.load(teamId: route.teamId) }
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

    // MARK: - Loaded

    private func loadedContent(_ detail: TeamDetailResponse) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.lg) {
                summaryRow(detail)
                    .modifier(EntranceAppear(visible: hasAppeared, reduceMotion: reduceMotion))
                transactionList(for: detail)
            }
            .padding(DSSpacingSwiftUI.md)
        }
        // The section selector now lives in the toolbar; a change still fires
        // the guarded haptic and the list swap below animates.
        .onChange(of: section) { _, _ in
            triggerHaptic()
        }
    }

    /// Three glass mini-cards: Saldo actual / Gastado / Ingresado. The numbers
    /// animate with `.contentTransition(.numericText())` when the detail loads.
    private func summaryRow(_ detail: TeamDetailResponse) -> some View {
        HStack(spacing: DSSpacingSwiftUI.sm) {
            summaryCard(
                title: "ACTUAL",
                value: MoneyFormatter.format(detail.balance, signed: false),
                color: detail.balance < 0 ? DSColor.moneyNegative : DSColor.moneyPositive,
                spokenSign: detail.balance < 0 ? "negativo" : "positivo"
            )
            summaryCard(
                title: "GASTADO",
                value: MoneyFormatter.format(detail.totalSpent, signed: false),
                color: DSColor.onSurface,
                spokenSign: nil
            )
            summaryCard(
                title: "INGRESADO",
                value: MoneyFormatter.format(detail.totalIncome, signed: false),
                color: DSColor.moneyPrize,
                spokenSign: nil
            )
        }
    }

    private func summaryCard(
        title: String,
        value: String,
        color: Color,
        spokenSign: String?
    ) -> some View {
        NeonGlassCard {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
                DSStatLabel(title)
                Text(value)
                    .font(DSFont.h3)
                    .foregroundStyle(color)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
                    .contentTransition(.numericText())
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(
            spokenSign == nil
                ? "\(title.capitalized) \(value)"
                : "\(title.capitalized) \(value) \(spokenSign!)"
        )
    }

    /// The chosen section's list (Compras | Ventas). The section is selected
    /// from the toolbar glass menu; a change fires a subtle guarded haptic and
    /// this list swaps with a sliding/opacity transition. On a fresh load the
    /// rows enter staggered by index for a soft landing.
    @ViewBuilder
    private func transactionList(for detail: TeamDetailResponse) -> some View {
        let items = section == .purchases ? detail.purchases : detail.sales
        let isPurchase = section == .purchases

        if items.isEmpty {
            Text(isPurchase ? "No hay compras registradas." : "No hay ventas registradas.")
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurfaceVariant)
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(.vertical, DSSpacingSwiftUI.lg)
                .accessibilityLabel(
                    isPurchase ? "No hay compras registradas" : "No hay ventas registradas"
                )
                .transition(.opacity)
        } else {
            VStack(spacing: DSSpacingSwiftUI.sm) {
                ForEach(Array(items.enumerated()), id: \.element.id) { index, transaction in
                    TeamDetailTransactionRow(
                        transaction: transaction,
                        isPurchase: isPurchase,
                        index: index
                    )
                    .modifier(
                        EntranceAppear(
                            visible: hasAppeared,
                            reduceMotion: reduceMotion,
                            delay: Self.staggerDelay(for: index)
                        )
                    )
                }
            }
            .animation(.easeInOut, value: section)
            .transition(.opacity)
        }
    }

    /// Per-row stagger: an incremental delay by row index so the rows settle
    /// in sequence (a soft landing, not a pop), capped so long lists do not
    /// trail on forever.
    private static func staggerDelay(for index: Int) -> Double {
        min(Double(index) * 0.05, 0.6)
    }

    // MARK: - Haptics (guarded)

    private func triggerHaptic() {
        #if canImport(UIKit)
        // The enclosing view is already iOS 17+, so no inner availability
        // check is needed. A one-shot light impact keeps the feedback local to
        // the section switch.
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
        #endif
    }
}

/// Gentle fade + slight upward slide entrance for the loaded content
/// (iteración 2e). Driven by `visible` (flipped when the VM reaches `.loaded`),
/// with an optional per-row `delay` so the transaction rows stagger into a soft
/// landing rather than popping. Under Reduce Motion the content is shown
/// immediately with no offset or animation (NFR5 / accessibility). The modifier
/// never moves the content once settled, so it does not interfere with the
/// summary numbers' `.contentTransition(.numericText())`.
@available(iOS 17.0, macOS 14.0, *)
private struct EntranceAppear: ViewModifier {
    let visible: Bool
    let reduceMotion: Bool
    var delay: Double = 0

    func body(content: Content) -> some View {
        if reduceMotion {
            content
        } else {
            content
                .opacity(visible ? 1 : 0)
                .offset(y: visible ? 0 : 8)
                .animation(.easeOut(duration: 0.4).delay(delay), value: visible)
        }
    }
}

/// A compact NeonGlass row for one market operation (FR6): player name (white),
/// price with a money token (purchases negative/red, sales positive/green),
/// from/to secondary, date formatted dd/MM/yyyy from the ISO string. The money
/// sign is the non-colour carrier of meaning (A7).
@available(iOS 15.0, macOS 12.0, *)
public struct TeamDetailTransactionRow: View {
    private let transaction: FutmondoKit.Transaction
    private let isPurchase: Bool
    private let index: Int

    public init(transaction: FutmondoKit.Transaction, isPurchase: Bool, index: Int) {
        self.transaction = transaction
        self.isPurchase = isPurchase
        self.index = index
    }

    /// Signed price: a purchase spends money (negative), a sale brings it in
    /// (positive). The sign is always present in the string (A7).
    private var signedPrice: Int { isPurchase ? -transaction.price : transaction.price }
    private var priceText: String { MoneyFormatter.format(signedPrice, signed: true) }
    private var priceColor: Color {
        isPurchase ? DSColor.moneyNegative : DSColor.moneyPositive
    }

    /// The counterparty: procedencia on a purchase, destino on a sale.
    private var counterparty: String? {
        isPurchase ? transaction.from : transaction.to
    }

    private var dateText: String { TransactionDatePresenter.display(transaction.date) }

    public var body: some View {
        NeonGlassCard {
            HStack(alignment: .center, spacing: DSSpacingSwiftUI.md) {
                VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
                    Text(transaction.playerName)
                        .font(DSFont.h3)
                        .foregroundStyle(DSColor.onSurface)
                        .lineLimit(1)
                    HStack(spacing: DSSpacingSwiftUI.xs) {
                        if let counterparty, !counterparty.isEmpty {
                            Text(counterparty)
                                .font(DSFont.body)
                                .foregroundStyle(DSColor.onSurfaceVariant)
                                .lineLimit(1)
                            Text("·")
                                .foregroundStyle(DSColor.onSurfaceVariant)
                        }
                        Text(dateText)
                            .font(DSFont.body)
                            .foregroundStyle(DSColor.onSurfaceVariant)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                Text(priceText)
                    .font(DSFont.h3)
                    .foregroundStyle(priceColor)
                    .lineLimit(1)
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityLabel)
    }

    private var accessibilityLabel: String {
        let sign = signedPrice < 0 ? "negativo" : "positivo"
        let origin: String
        if let counterparty, !counterparty.isEmpty {
            origin = isPurchase ? ", procedencia \(counterparty)" : ", destino \(counterparty)"
        } else {
            origin = ""
        }
        return "\(transaction.playerName), \(priceText) \(sign)\(origin), \(dateText)"
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
