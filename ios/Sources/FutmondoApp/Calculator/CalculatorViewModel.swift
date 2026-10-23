import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI
import Observation

/// Load state of the Calculadora screen (W1 / state machine in
/// functional-spec.md). `Equatable` so `CalculatorView` can drive
/// `.onChange`/animations. The `error` payload is a ready-to-show,
/// non-sensitive message (never a championship id or token).
public enum CalculatorLoadState: Equatable {
    case idle
    case loading
    case data
    case empty
    case error(String)
}

/// A transient, user-facing notice shown after a sell/cancel (W5/W6). Carries
/// only localized prose — never credential material.
public struct CalculatorNotice: Equatable, Identifiable {
    public enum Kind: Equatable { case success, info, error }
    public let id = UUID()
    public let kind: Kind
    public let message: String
}

/// Observable view model for the Calculadora screen (FR2–FR10).
///
/// Orchestrates `RosterService` + `MarketService` + the pure `FutmondoKit`
/// types (`CalculatorMath`, `CalculatorSorter`, `CalculatorPreferences`): loads
/// roster + economy + on-sale in parallel (BR11.1), recomposes the selectable
/// list in memory on toggle (BR5.2 / BR4.2), projects by date (BR1.1),
/// performs sell/cancel writes, and reloads only when the outcome requires it
/// (BR8.2 / BR9.1). All money rules live in unit-tested pure types; this type
/// is the SwiftUI-bound orchestration, validated on device.
@available(iOS 17.0, macOS 14.0, *)
@MainActor
@Observable
public final class CalculatorViewModel {
    public private(set) var loadState: CalculatorLoadState = .idle

    /// The recomposed SELECTABLE list (roster filtered + sorted per the toggle).
    public private(set) var players: [RosterPlayer] = []
    /// The raw roster as fetched (before toggle filtering).
    public private(set) var rawRoster: [RosterPlayer] = []
    public private(set) var onSalePlayers: [OnSalePlayer] = []
    public private(set) var economy: MarketUserInfo?

    public private(set) var selectedIds: Set<String> = []
    public private(set) var includeOnSale: Bool
    public private(set) var sortField: CalculatorSortField
    /// Days to project ahead (BR1.2), derived from the chosen date; always >= 0.
    public private(set) var daysAhead: Int = 0

    /// GLOBAL single-write guard: one sell/cancel at a time.
    public private(set) var isWriting: Bool = false
    public var lastNotice: CalculatorNotice?

    private let rosterService: any RosterService
    private let marketService: any MarketService
    private let activeStore: any ActiveChampionshipStore
    private let preferences: CalculatorPreferences

    // Localized (Spanish) notices.
    private let networkGeneric = "Error de conexión. Inténtalo de nuevo."
    private let cancelFallback = "No se pudo cancelar la venta."
    private let cancelSuccess = "Venta cancelada."

    private var freshness = DataFreshness()

    /// Called after an ACCEPTED sell/cancel so Presupuesto + Mercado invalidate
    /// their caches (BR10.1).
    private let onWriteAccepted: () -> Void

    public init(
        rosterService: any RosterService,
        marketService: any MarketService,
        activeStore: any ActiveChampionshipStore,
        preferences: CalculatorPreferences,
        onWriteAccepted: @escaping () -> Void = {}
    ) {
        self.rosterService = rosterService
        self.marketService = marketService
        self.activeStore = activeStore
        self.preferences = preferences
        self.includeOnSale = preferences.includeOnSale
        self.sortField = preferences.sortField
        self.onWriteAccepted = onWriteAccepted
    }

    public var activeChampionshipId: String? { activeStore.activeId }

    /// Ids of the players currently on sale (for anti-double-count filtering).
    private var onSaleIds: Set<String> { Set(onSalePlayers.map(\.playerId)) }

    // MARK: - Derived money figures (via CalculatorMath)

    public var selectedTotal: Int {
        CalculatorMath.selectedTotal(players: players, selectedIds: selectedIds, daysAhead: daysAhead)
    }

    public var onSaleTotal: Int { CalculatorMath.onSaleTotal(onSalePlayers) }

    public var futureBalance: Int {
        CalculatorMath.futureBalance(
            balance: economy?.balance ?? 0,
            selectedTotal: selectedTotal,
            onSaleTotal: onSaleTotal,
            includeOnSale: includeOnSale,
            activeBidsTotal: economy?.activeBidsTotal ?? 0
        )
    }

    public func projectedValue(for player: RosterPlayer) -> Int {
        CalculatorMath.projectedValue(player, daysAhead: daysAhead)
    }

    public var selectedCount: Int { selectedIds.count }

    // MARK: - Loading (BR11.1)

    public func loadIfNeeded() async {
        if freshness.shouldReload(activeId: activeStore.activeId) {
            await load()
        }
    }

    /// Load roster + economy + on-sale in parallel for the active championship
    /// (W1 / BR11.1). Replaces state wholesale; never merges.
    public func load() async {
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else {
            rawRoster = []
            players = []
            onSalePlayers = []
            economy = nil
            loadState = .empty
            return
        }

        loadState = .loading
        do {
            // Three concurrent requests (BR11.1).
            async let rosterTask = rosterService.fetchRoster(championshipId: championshipId)
            async let economyTask = marketService.loadToday(championshipId: championshipId)
            async let onSaleTask = rosterService.fetchOnSale(championshipId: championshipId)

            let roster = try await rosterTask
            let today = try await economyTask
            let onSale = try await onSaleTask

            rawRoster = roster
            onSalePlayers = onSale
            economy = today.userInfo
            recomposeSelectable()

            loadState = rawRoster.isEmpty ? .empty : .data
            freshness.markLoaded(championshipId: championshipId)
        } catch {
            // Verbatim, non-sensitive message; never interpolate id/tokens.
            loadState = .error(error.localizedDescription)
        }
    }

    public func reload() async { await load() }

    public func invalidate() { freshness.invalidate() }

    // MARK: - Selectable composition (BR4.1 / BR5.2)

    /// Recompose the selectable list in memory (no network). With the toggle
    /// ON, on-sale players are EXCLUDED (they count via onSaleTotal); with OFF,
    /// the full roster is selectable (BR5.2). The list is then sorted (W7).
    private func recomposeSelectable() {
        let base: [RosterPlayer]
        if includeOnSale {
            let onSale = onSaleIds
            base = rawRoster.filter { !onSale.contains($0.playerId) }
        } else {
            base = rawRoster
        }
        players = CalculatorSorter.sorted(base, by: sortField, daysAhead: daysAhead)
    }

    // MARK: - Interactions

    /// Tap a card: toggle its selection (W2 / FR6.1).
    public func toggleSelection(_ playerId: String) {
        if selectedIds.contains(playerId) {
            selectedIds.remove(playerId)
        } else {
            selectedIds.insert(playerId)
        }
    }

    /// Select every currently selectable player (FR6.2).
    public func selectAll() {
        selectedIds = Set(players.map(\.playerId))
    }

    /// Clear the whole selection (FR6.2).
    public func deselectAll() {
        selectedIds.removeAll()
    }

    /// Change the "incorporar en venta" toggle (W4). Persists it, purges any
    /// on-sale selection on the OFF→ON transition (BR4.2), and recomposes.
    public func setIncludeOnSale(_ newValue: Bool) {
        let wasOff = !includeOnSale
        includeOnSale = newValue
        preferences.includeOnSale = newValue
        // BR4.2: turning the toggle ON discards any manual selection of on-sale
        // players so their value counts only via onSaleTotal.
        if wasOff && newValue {
            selectedIds.subtract(onSaleIds)
        }
        recomposeSelectable()
    }

    /// Change the projection days (W3 / BR1.2). Clamped to >= 0; recomposes so a
    /// projectedValue sort reorders.
    public func setDaysAhead(_ days: Int) {
        daysAhead = max(0, days)
        recomposeSelectable()
    }

    /// Change the sort field (W7 / FR5.3). Persists it and reorders in memory.
    public func setSort(_ field: CalculatorSortField) {
        sortField = field
        preferences.sortField = field
        recomposeSelectable()
    }

    // MARK: - Writes (W5 / W6)

    /// Put the selected players on sale (W5 / FR8). No-op while writing or with
    /// no selection (BR8.1). Only a `.total` outcome removes players + reloads
    /// on-sale (BR8.2); `.partial`/`.none` only inform.
    public func sellSelected() async {
        guard !isWriting else { return }
        guard !selectedIds.isEmpty else { return }
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else { return }

        let ids = Array(selectedIds)
        isWriting = true
        let outcome = await rosterService.sell(
            championshipId: championshipId,
            playerIds: ids,
            genericNetwork: networkGeneric
        )
        isWriting = false

        switch outcome {
        case .total(let sold):
            lastNotice = CalculatorNotice(kind: .success, message: "Añadidos \(sold) jugador(es) al mercado.")
            selectedIds.removeAll()
            onWriteAccepted()
            await reload()
        case .partial(let sold, let total):
            // Inform only; do NOT remove or reload (BR8.2 / R-02).
            lastNotice = CalculatorNotice(kind: .info, message: "Añadidos al mercado \(sold) de \(total).")
        case .none(let total):
            lastNotice = CalculatorNotice(kind: .error, message: "No se añadió a la venta ninguno de \(total).")
        case .networkError(let message):
            lastNotice = CalculatorNotice(kind: .error, message: message)
        }
    }

    /// Cancel a player's sale (W6 / FR9). No-op while writing. Reloads on an
    /// accepted cancel (BR9.1) and invalidates caches (BR10.1).
    public func cancelSale(playerId: String) async {
        guard !isWriting else { return }
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else { return }

        isWriting = true
        let outcome = await rosterService.cancelSale(
            championshipId: championshipId,
            playerId: playerId,
            fallbackRejection: cancelFallback,
            genericNetwork: networkGeneric
        )
        isWriting = false

        switch outcome {
        case .accepted:
            lastNotice = CalculatorNotice(kind: .success, message: cancelSuccess)
            onWriteAccepted()
            await reload()
        case .rejected(let message):
            lastNotice = CalculatorNotice(kind: .error, message: message)
        case .networkError:
            lastNotice = CalculatorNotice(kind: .error, message: networkGeneric)
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
