import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI
import Observation

/// UI state of the budget screen (US1 / FR1, FR3, FR4).
///
/// `Equatable` so `BudgetView` can drive `.onChange`/animations and tests can
/// assert the exact state on device. The `error` payload is a ready-to-show,
/// non-sensitive message (never a championship id or token).
public enum BudgetState: Equatable {
    case loading
    case loaded([TeamBudget])
    case emptyTeams
    case noChampionships
    case error(String)
}

/// Observable view model for the budget screen (C-U2 / FR1-FR4).
///
/// Orchestrates the U1 services and store: it fetches the user's championships,
/// resolves and persists the active one, fetches its balances, and sorts the
/// rows. All pure logic (resolution, persistence decision, sorting,
/// formatting) lives in `FutmondoKit` and is unit-tested there; this type is
/// the SwiftUI-bound orchestration, validated on device (iPhone 13 Pro).
@available(iOS 17.0, macOS 14.0, *)
@MainActor
@Observable
public final class BudgetViewModel {
    /// Current screen state. Starts at `.loading`; `load()` resolves it.
    public private(set) var state: BudgetState = .loading

    /// The user's championships (empty until the first successful fetch).
    public private(set) var championships: [Championship] = []

    /// The resolved active championship, or `nil` when there are none.
    public private(set) var activeChampionship: Championship?

    /// The active sort key (always descending — the ascending toggle is a
    /// deferred follow-up, interaction-spec). Defaults to `.balance`.
    public private(set) var sortKey: SortKey = .balance

    private let budgetService: any BudgetService
    private let championshipService: any ChampionshipService
    private let activeStore: any ActiveChampionshipStore

    /// In-memory freshness so returning to the budget tab does not refetch the
    /// API every time (TTL + per-championship).
    private var freshness = DataFreshness()

    public init(
        budgetService: any BudgetService,
        championshipService: any ChampionshipService,
        activeStore: any ActiveChampionshipStore
    ) {
        self.budgetService = budgetService
        self.championshipService = championshipService
        self.activeStore = activeStore
    }

    /// Load only when the in-memory cache is stale (different championship, past
    /// the TTL, never loaded, or invalidated). Called from `.task` on appear so
    /// switching tabs reuses the cached budget instead of refetching.
    public func loadIfNeeded() async {
        if freshness.shouldReload(activeId: activeStore.activeId) {
            await load()
        }
    }

    /// Drop the in-memory freshness so the next `loadIfNeeded()` refetches
    /// (used for cross-screen invalidation after a market write).
    public func invalidate() { freshness.invalidate() }

    /// Load the active championship's budget (FR1, FR3, FR4).
    ///
    /// Flow:
    /// 1. `state = .loading` synchronously, before any `await`, so the spinner
    ///    shows within <100 ms (NFR4).
    /// 2. Fetch championships. On throw → `.error` WITHOUT touching the stored
    ///    active id (FR4.2 — a failure never corrupts persistence).
    /// 3. Empty list → `.noChampionships`.
    /// 4. Resolve the active one (`ActiveChampionshipResolver`); persist it only
    ///    when it changed (`ActiveChampionshipPersistence`, FR3.3).
    /// 5. Fetch its balances → `.loaded` (sorted) / `.emptyTeams` / `.error`.
    public func load() async {
        state = .loading

        let fetched: [Championship]
        do {
            fetched = try await championshipService.fetchChampionships()
        } catch {
            // Do NOT mutate the persisted active id on a fetch failure (FR4.2).
            state = .error(error.localizedDescription)
            return
        }

        championships = fetched

        guard let resolved = ActiveChampionshipResolver.resolve(
            activeId: activeStore.activeId,
            in: fetched
        ) else {
            activeChampionship = nil
            state = .noChampionships
            return
        }

        activeChampionship = resolved
        if ActiveChampionshipPersistence.shouldPersist(
            resolvedId: resolved.championshipId,
            storedId: activeStore.activeId
        ) {
            activeStore.setActive(resolved.championshipId)
        }

        await loadBalances(for: resolved.championshipId)
    }

    /// Select a different championship (US2 / FR3): persist the choice and
    /// reload. Persisting first keeps the selection durable even if the
    /// balances fetch then fails (FR4.2 — the chosen id is what the user asked
    /// for, not a resolution side effect).
    public func selectChampionship(_ championship: Championship) async {
        guard championship.championshipId != activeChampionship?.championshipId else {
            return
        }
        activeStore.setActive(championship.championshipId)
        activeChampionship = championship
        state = .loading
        await loadBalances(for: championship.championshipId)
    }

    /// Change the sort key (US3 / FR2.1). Reorders the current rows in place
    /// when loaded; otherwise it just records the key so the next `.loaded`
    /// applies it.
    public func setSort(_ key: SortKey) {
        sortKey = key
        if case .loaded(let teams) = state {
            state = .loaded(TeamBudgetSort.sorted(teams, by: key))
        }
    }

    // MARK: - Private

    /// Fetch and map balances for a championship. State is already `.loading`.
    private func loadBalances(for championshipId: String) async {
        do {
            let response = try await budgetService.fetchBalances(championshipId: championshipId)
            if response.teams.isEmpty {
                state = .emptyTeams
            } else {
                state = .loaded(TeamBudgetSort.sorted(response.teams, by: sortKey))
            }
            // Successful fetch → cache is fresh for this championship.
            freshness.markLoaded(championshipId: championshipId)
        } catch {
            // Verbatim, non-sensitive message; never interpolate the id/tokens.
            state = .error(error.localizedDescription)
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
