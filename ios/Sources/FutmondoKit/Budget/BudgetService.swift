import Foundation

/// Fetches team balances for a championship (R3 / FR1.1, FR4.2) and one team's
/// detail (FR6).
public protocol BudgetService: Sendable {
    func fetchBalances(championshipId: String) async throws -> BalancesResponse
    /// Fetch one team's market detail (purchases/sales) for a championship
    /// (FR6). Same typed-error / no-leak guarantees as ``fetchBalances``.
    func fetchTeamDetail(teamId: String, championshipId: String) async throws -> TeamDetailResponse
}

/// `NetworkClient`-backed ``BudgetService``. Consumes the F1 transport; adds no
/// new dependency and never logs or embeds credentials in errors (SR1).
public struct HTTPBudgetService: BudgetService {
    private let network: any NetworkClient

    public init(network: any NetworkClient) {
        self.network = network
    }

    public func fetchBalances(championshipId: String) async throws -> BalancesResponse {
        // The championship id is carried as a query parameter. It is not a
        // secret, but the typed NetworkError below never echoes the full URL
        // or query, so a failed call cannot leak it (SR1).
        let request = APIRequest(
            method: .get,
            path: "/api/v1/analytics/balances?championship_id=\(championshipId)"
        )
        let result: Result<BalancesResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            return response
        case .failure(let error):
            throw error
        }
    }

    public func fetchTeamDetail(
        teamId: String,
        championshipId: String
    ) async throws -> TeamDetailResponse {
        // The team id is a path segment and the championship id a query
        // parameter; neither is a secret, and the typed NetworkError below
        // never echoes the full URL or query, so a failed call cannot leak
        // either (SR1).
        let request = APIRequest(
            method: .get,
            path: "/api/v1/analytics/balances/\(teamId)?championship_id=\(championshipId)"
        )
        let result: Result<TeamDetailResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            return response
        case .failure(let error):
            throw error
        }
    }
}
