import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI
import Observation

/// UI state of the team-detail screen (FR6).
///
/// `Equatable` so `TeamDetailView` can drive `.onChange`/animations and tests
/// can assert the exact state on device. The `loaded` payload is
/// ``TeamDetailResponse`` (itself `Equatable`); the `error` payload is a
/// ready-to-show, non-sensitive message (never a team/championship id or
/// token).
public enum TeamDetailState: Equatable {
    case loading
    case loaded(TeamDetailResponse)
    case error(String)
}

/// Observable view model for the team-detail screen (FR6).
///
/// It fetches one team's market detail (purchases/sales) for the active
/// championship, resolved from the injected ``ActiveChampionshipStore`` so the
/// detail always matches the budget list's selection. All transport and error
/// mapping live in U1 (`HTTPBudgetService` + typed `NetworkError`); this type
/// is the SwiftUI-bound orchestration, validated on device (iPhone 13 Pro).
@available(iOS 17.0, macOS 14.0, *)
@MainActor
@Observable
public final class TeamDetailViewModel {
    /// Current screen state. Starts at `.loading`; `load(teamId:)` resolves it.
    public private(set) var state: TeamDetailState = .loading

    private let budgetService: any BudgetService
    private let activeStore: any ActiveChampionshipStore

    public init(
        budgetService: any BudgetService,
        activeStore: any ActiveChampionshipStore
    ) {
        self.budgetService = budgetService
        self.activeStore = activeStore
    }

    /// Load the team's detail for the active championship (FR6).
    ///
    /// Sets `.loading` synchronously before any `await` so the spinner shows
    /// immediately. When no active championship is stored (should not happen
    /// from the budget list), it maps to a verbatim, non-sensitive error rather
    /// than issuing a call with an empty id. The error string is taken verbatim
    /// from the U1 typed error (`error.localizedDescription`) and never
    /// interpolates the team or championship id (SR1).
    public func load(teamId: String) async {
        state = .loading

        guard let championshipId = activeStore.activeId else {
            state = .error("No hay campeonato activo.")
            return
        }

        do {
            let response = try await budgetService.fetchTeamDetail(
                teamId: teamId,
                championshipId: championshipId
            )
            state = .loaded(response)
        } catch {
            state = .error(error.localizedDescription)
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
