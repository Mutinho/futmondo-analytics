import Foundation

/// Dedicated service for the Sofascore player-detail fetch (FR8 / W7 / C8).
///
/// Separate from ``MarketService`` by design (FR8.2 / BR-UI-5): the detail call
/// hits a different endpoint (`/api/v1/sofascore/player/{name}`, NOT `/market`)
/// and its result lives in sheet-local state, so a failure or latency here can
/// never degrade the market list or bidding. An `actor` for the same reasons as
/// `MarketService`.
public protocol SofascoreService: Sendable {
    /// `GET /api/v1/sofascore/player/{player_name}?championship_id=<id>` (W7).
    ///
    /// Returns a typed ``SofascoreDetailOutcome`` (never throws): 2xx →
    /// `.loaded`, 404 → `.empty` ("sin datos"), any other failure → `.failed`.
    func loadDetail(
        playerName: String,
        championshipId: String
    ) async -> SofascoreDetailOutcome
}

/// `NetworkClient`-backed ``SofascoreService``.
public actor HTTPSofascoreService: SofascoreService {
    private let network: any NetworkClient

    public init(network: any NetworkClient) {
        self.network = network
    }

    public func loadDetail(
        playerName: String,
        championshipId: String
    ) async -> SofascoreDetailOutcome {
        // The player name is a PATH segment; percent-encode it so a name with
        // spaces/accents yields a valid URL.
        let encodedName = playerName
            .addingPercentEncoding(withAllowedCharacters: .urlPathSegmentAllowed) ?? playerName
        let request = APIRequest(
            method: .get,
            path: "/api/v1/sofascore/player/\(encodedName)?championship_id=\(encodeQuery(championshipId))"
        )
        let result: Result<SofascoreDetailResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            // The backend nests the stats under `player`; unwrap it. A 2xx with
            // no player (success:false) is treated as "no data".
            if let detail = response.player {
                return .loaded(detail)
            }
            return .empty
        case .failure(let error):
            // 404 means "no Sofascore row" → treated as empty, not an error
            // (W7). Everything else is a local failure that stays in the sheet.
            if case .clientError(404) = error {
                return .empty
            }
            return .failed
        }
    }

    private func encodeQuery(_ value: String) -> String {
        value.addingPercentEncoding(withAllowedCharacters: .sofascoreQueryValueAllowed) ?? value
    }
}

extension CharacterSet {
    fileprivate static let urlPathSegmentAllowed: CharacterSet = {
        var set = CharacterSet.urlPathAllowed
        // A single path segment must not contain `/` or `?`.
        set.remove(charactersIn: "/?")
        return set
    }()

    fileprivate static let sofascoreQueryValueAllowed: CharacterSet = {
        var set = CharacterSet.urlQueryAllowed
        set.remove(charactersIn: "&=+?")
        return set
    }()
}
