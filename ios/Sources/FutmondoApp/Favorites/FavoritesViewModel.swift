import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI
import Observation

/// Load state of the Favoritos screen (W1 / functional-spec.md state machine).
/// `Equatable` so `FavoritesView` can drive `.onChange`/animations. The `error`
/// payload is a ready-to-show, non-sensitive message (never a championship id
/// or token).
public enum FavoritesLoadState: Equatable {
    case idle
    case loading
    case data
    case empty
    case error(String)
}

/// A transient, user-facing notice shown after an unfollow (W4). Carries only
/// the backend's own prose or a localized generic/success message — never
/// credential material.
public struct FavoritesNotice: Equatable, Identifiable {
    public enum Kind: Equatable { case rejected, networkError }
    public let id = UUID()
    public let kind: Kind
    public let message: String
}

/// Observable view model for the Favoritos screen (V1 / FR1–FR7).
///
/// Orchestrates `FavoritesService` + `FavoritesSorter` + the persisted
/// `FavoritesPreferences`: loads the list, sorts in memory on sort change (no
/// reload), performs the unfollow write behind a single `isWriting` guard
/// (BR5.3), reloads ONLY on an `.accepted` outcome (BR5.2), and keeps the list
/// intact on a `.rejected`/`.networkError` outcome (BR5.4). All business rules
/// live in pure, unit-tested `FutmondoKit` types; this type is the SwiftUI-
/// bound orchestration, validated on device.
///
/// The active championship id is read from the SAME `ActiveChampionshipStore`
/// the budget screen uses, so switching the championship elsewhere is picked up
/// on the next `load()`.
@available(iOS 17.0, macOS 14.0, *)
@MainActor
@Observable
public final class FavoritesViewModel {
    public private(set) var loadState: FavoritesLoadState = .idle
    public private(set) var players: [FavoritePlayer] = []
    public private(set) var sortField: FavoritesSortField
    /// Single-write guard (BR5.3): one unfollow at a time disables every card's
    /// remove affordance while a write is in flight.
    public private(set) var isWriting: Bool = false
    /// The latest write notice to surface (success / rejection / network).
    public var lastNotice: FavoritesNotice?

    private let favoritesService: any FavoritesService
    private let activeStore: any ActiveChampionshipStore
    private let preferences: FavoritesPreferences

    // Localized (Spanish) notices — kept here so no English leaks into the UI
    // and no credential material is ever synthesized.
    private let rejectionFallback = "No se pudo quitar de favoritos."
    private let networkGeneric = "Error de conexión. Inténtalo de nuevo."

    /// In-memory freshness so returning to this tab does not refetch the API
    /// every time (TTL + per-championship).
    private var freshness = DataFreshness()

    public init(
        favoritesService: any FavoritesService,
        activeStore: any ActiveChampionshipStore,
        preferences: FavoritesPreferences
    ) {
        self.favoritesService = favoritesService
        self.activeStore = activeStore
        self.preferences = preferences
        self.sortField = preferences.sortField
    }

    /// The championship id in effect for the next request, or `nil` when none
    /// is selected yet.
    public var activeChampionshipId: String? { activeStore.activeId }

    /// Load only when the in-memory cache is stale (different championship, past
    /// the TTL, never loaded, or invalidated). Called from `.task` on appear so
    /// switching tabs reuses the cached list instead of refetching (BR1.1).
    public func loadIfNeeded() async {
        if freshness.shouldReload(activeId: activeStore.activeId) {
            await load()
        }
    }

    /// Load (or reload) the favourites for the active championship (W1 /
    /// BR1.1). Replaces `players` wholesale; never merges. Sets `.loading`
    /// synchronously before any `await` so the spinner shows immediately.
    public func load() async {
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else {
            // No active championship → nothing to show; treat as empty rather
            // than a hard error (the budget tab owns championship selection).
            players = []
            loadState = .empty
            return
        }

        loadState = .loading
        do {
            let favorites = try await favoritesService.fetchFavorites(championshipId: championshipId)
            if favorites.isEmpty {
                players = []
                loadState = .empty
            } else {
                players = FavoritesSorter.sorted(favorites, by: sortField)
                loadState = .data
            }
            // Successful fetch → cache is fresh for this championship.
            freshness.markLoaded(championshipId: championshipId)
        } catch {
            // Verbatim, non-sensitive message; never interpolate id/tokens.
            loadState = .error(error.localizedDescription)
        }
    }

    /// Change the sort field (W3 / FR4): reorders the already-loaded list in
    /// memory with no network call, and persists the choice (BR4.1).
    public func setSort(_ field: FavoritesSortField) {
        sortField = field
        preferences.sortField = field
        guard loadState == .data else { return }
        players = FavoritesSorter.sorted(players, by: field)
    }

    /// Remove a player from favourites (W4 / FR5). No-op if another write is in
    /// flight (BR5.3). On `.accepted` the player is removed from the in-memory
    /// list with NO refetch (BR5.2, optimistic local removal — the caller wraps
    /// this in `withAnimation` for a smooth reflow); on
    /// `.rejected`/`.networkError` the list stays intact and the action is
    /// re-enabled (BR5.4).
    public func unfollow(player: FavoritePlayer) async {
        guard !isWriting else { return }
        guard let championshipId = activeStore.activeId, !championshipId.isEmpty else { return }

        isWriting = true
        let outcome = await favoritesService.unfollow(
            championshipId: championshipId,
            playerId: player.playerId,
            fallbackRejection: rejectionFallback,
            genericNetwork: networkGeneric
        )
        // Re-enable the action regardless of the outcome (BR5.4): the guard is
        // released before any reload so the UI is never left disabled.
        isWriting = false

        switch outcome {
        case .accepted:
            // No success alert: the animated card removal already communicates
            // it (owner feedback). Only failures surface a notice (BR5.4).
            // Optimistic LOCAL removal (BR5.2): drop the player from the
            // in-memory list — no refetch. The caller mutates inside
            // `withAnimation` so the remaining cards reflow smoothly. If the
            // list becomes empty, fall to the empty state. Unfollowing a
            // favourite changes no economy figures, so no cross-screen
            // invalidation is needed (FR7.1).
            players.removeAll { $0.playerId == player.playerId }
            if players.isEmpty { loadState = .empty }
        case .rejected(let message):
            // List intact; inform only (BR5.4).
            lastNotice = FavoritesNotice(kind: .rejected, message: message)
        case .networkError:
            // List intact; generic notice (BR5.4).
            lastNotice = FavoritesNotice(kind: .networkError, message: networkGeneric)
        }
    }

    /// Drop the in-memory freshness so the next `loadIfNeeded()` refetches.
    public func invalidate() { freshness.invalidate() }
}

#endif // canImport(SwiftUI) && canImport(Observation)
