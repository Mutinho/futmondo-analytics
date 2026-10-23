import Foundation

/// Fetches the user's championships, with an internal fallback (R4 / FR3.1,
/// FR4.2).
public protocol ChampionshipService: Sendable {
    func fetchChampionships() async throws -> [Championship]
}

/// `NetworkClient`-backed ``ChampionshipService``.
///
/// Tries `GET /api/v1/user/championships` first; on **any** error (transport,
/// non-2xx status, or a decoding failure) it falls back to
/// `GET /api/v1/championships`. If the fallback also fails, the fallback's
/// error is propagated. It never returns a silent partial list.
public struct HTTPChampionshipService: ChampionshipService {
    private let network: any NetworkClient

    private static let primaryPath = "/api/v1/user/championships"
    private static let fallbackPath = "/api/v1/championships"

    public init(network: any NetworkClient) {
        self.network = network
    }

    public func fetchChampionships() async throws -> [Championship] {
        do {
            return try await fetch(path: Self.primaryPath)
        } catch {
            // Primary failed for any reason (network, status, or decode):
            // try the fallback. If it also throws, propagate THAT error.
            return try await fetch(path: Self.fallbackPath)
        }
    }

    private func fetch(path: String) async throws -> [Championship] {
        let request = APIRequest(method: .get, path: path)
        let result: Result<ChampionshipsResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            return response.championships
        case .failure(let error):
            throw error
        }
    }
}
