import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI
import Observation

/// Load state of the market screen (W1 / FR2). `Equatable` so `MarketView` can
/// drive `.onChange`/animations. The `error` payload is a ready-to-show,
/// non-sensitive message (never a championship id or token).
public enum MarketLoadState: Equatable {
    case idle
    case loading
    case data
    case empty
    case error(String)
}

/// A transient, user-facing notice shown after a write (W6). Carries only the
/// backend's own prose or a localized generic/success message — never
/// credential material.
public struct MarketWriteNotice: Equatable, Identifiable {
    public enum Kind: Equatable { case success, rejected, networkError }
    public let id = UUID()
    public let kind: Kind
    public let message: String
}

/// Observable view model for the market screen (V2 / FR2–FR7).
///
/// Orchestrates `MarketService` + `MarketSorter`: loads the page, sorts in
/// memory on sort change (no reload), performs bid/cancel writes behind a
/// GLOBAL `isWriting` flag (BR-UI-4), and reloads ONLY on an `.accepted`
/// outcome (BR-UI-3). All business rules live in pure `FutmondoKit` types
/// (`MarketSorter`, `BidAmountValidator`, `MarketWriteOutcome`) unit-tested
/// there; this type is the SwiftUI-bound orchestration, validated on device.
///
/// The active championship id is read from the SAME `ActiveChampionshipStore`
/// the budget screen uses, so switching the championship elsewhere is picked up
/// on the next `load()`.
@available(iOS 17.0, macOS 14.0, *)
@MainActor
@Observable
public final class MarketViewModel {
    public private(set) var loadState: MarketLoadState = .idle
    public private(set) var players: [MarketPlayer] = []
    public private(set) var userInfo: MarketUserInfo?
    public private(set) var sortField: MarketSortField = .defaultField
    /// GLOBAL single-write guard (BR-UI-4): one bid/cancel at a time disables
    /// every card's write affordance while a write is in flight.
    public private(set) var isWriting: Bool = false
    /// The latest write notice to surface (success / rejection / network).
    public var lastWriteNotice: MarketWriteNotice?

    private let marketService: any MarketService
    private let activeStore: any ActiveChampionshipStore

    // Localized (Spanish) notices — kept here so no English leaks into the UI
    // and no credential material is ever synthesized.
    private let rejectionFallback = "No se pudo completar la operación."
    private let networkGeneric = "Error de conexión. Inténtalo de nuevo."
    private let bidSuccess = "Puja registrada."
    private let cancelSuccess = "Puja cancelada."

    /// In-memory freshness so returning to this tab does not refetch the API
    /// every time (TTL + per-championship).
    private var freshness = DataFreshness()

    /// Called after an ACCEPTED write (bid/cancel) so the other screen (budget)
    /// can invalidate its own freshness — the economy figures changed.
    private let onWriteAccepted: () -> Void

    public init(
        marketService: any MarketService,
        activeStore: any ActiveChampionshipStore,
        onWriteAccepted: @escaping () -> Void = {}
    ) {
        self.marketService = marketService
        self.activeStore = activeStore
        self.onWriteAccepted = onWriteAccepted
    }

    /// The championship id in effect for the next request, or `nil` when none
    /// is selected yet.
    public var activeChampionshipId: String? { activeStore.activeId }

    /// Load only when the in-memory cache is stale (different championship, past
    /// the TTL, never loaded, or invalidated). Called from `.task` on appear so
    /// switching tabs reuses the cached page instead of refetching (the market
    /// data stays put until it is actually stale).
    public func loadIfNeeded() async {
        if freshness.shouldReload(activeId: activeStore.activeId) {
            await load()
        }
    }

    /// Load (or reload) the market for the active championship (W1). Replaces
    /// `players` + `userInfo` wholesale; never merges. Sets `.loading`
    /// synchronously before any `await` so the spinner shows immediately.
    public func load() async {
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else {
            // No active championship → nothing to show; treat as empty rather
            // than a hard error (the budget tab owns championship selection).
            players = []
            userInfo = nil
            loadState = .empty
            return
        }

        loadState = .loading
        do {
            let response = try await marketService.loadToday(championshipId: championshipId)
            userInfo = response.userInfo
            if response.players.isEmpty {
                players = []
                loadState = .empty
            } else {
                players = MarketSorter.sorted(response.players, by: sortField)
                loadState = .data
            }
            // Successful fetch → cache is fresh for this championship.
            freshness.markLoaded(championshipId: championshipId)
        } catch {
            // Verbatim, non-sensitive message; never interpolate id/tokens.
            loadState = .error(error.localizedDescription)
        }
    }

    /// Explicit reload alias (W1 / BR-UI-3), used after an `.accepted` write.
    public func reload() async { await load() }

    /// Change the sort field (W3 / FR5): reorders the already-loaded list in
    /// memory with no network call. Ephemeral — not persisted.
    public func setSort(_ field: MarketSortField) {
        sortField = field
        guard loadState == .data else { return }
        players = MarketSorter.sorted(players, by: field)
    }

    /// Place a bid (W4 / FR6). No-op if another write is in flight (BR-UI-4).
    /// Reloads only on `.accepted` (BR-UI-3).
    public func placeBid(player: MarketPlayer, price: Int) async {
        guard !isWriting else { return }
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else { return }

        isWriting = true
        let outcome = await marketService.placeBid(
            championshipId: championshipId,
            playerId: player.playerId,
            playerSlug: player.slug,
            price: price,
            fallbackRejection: rejectionFallback,
            genericNetwork: networkGeneric
        )
        isWriting = false
        await apply(outcome: outcome, successMessage: bidSuccess)
    }

    /// Cancel the player's active bid (W5 / FR7). No-op if another write is in
    /// flight (BR-UI-4) or the player has no active bid id. Reloads only on
    /// `.accepted` (BR-UI-3).
    public func cancelBid(player: MarketPlayer) async {
        guard !isWriting else { return }
        guard let bidId = player.currentBidId else { return }
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else { return }

        isWriting = true
        let outcome = await marketService.cancelBid(
            championshipId: championshipId,
            bidId: bidId,
            fallbackRejection: rejectionFallback,
            genericNetwork: networkGeneric
        )
        isWriting = false
        await apply(outcome: outcome, successMessage: cancelSuccess)
    }

    /// Map a write outcome to a notice and decide the reload (W6 / BR-UI-3).
    private func apply(outcome: MarketWriteOutcome, successMessage: String) async {
        switch outcome {
        case .accepted:
            lastWriteNotice = MarketWriteNotice(kind: .success, message: successMessage)
            // The accepted bid/cancel reloads THIS screen and changes the
            // economy figures the budget screen also shows → invalidate it so
            // it refetches when next shown (cross-screen coherence).
            onWriteAccepted()
            await reload()
        case .rejected(let message):
            lastWriteNotice = MarketWriteNotice(kind: .rejected, message: message)
        case .networkError:
            lastWriteNotice = MarketWriteNotice(kind: .networkError, message: networkGeneric)
        }
    }

    /// Drop the in-memory freshness so the next `loadIfNeeded()` refetches
    /// (used for cross-screen invalidation after a write elsewhere).
    public func invalidate() { freshness.invalidate() }
}

#endif // canImport(SwiftUI) && canImport(Observation)
