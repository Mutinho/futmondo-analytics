import Foundation

/// Fetches the user's favourite free players and performs the unfollow write
/// (FR1.1 / FR5 / C1). An `actor` so concurrent calls are serialized on its
/// executor; it owns no mutable state beyond the injected transport.
///
/// Consumes the F1 ``NetworkClient`` (Bearer injected by the transport, SEC /
/// NFR3); it adds no dependency and never logs or embeds credentials in
/// errors. The backend contract is INMUTABLE (C1 / BR8.1): the exact paths
/// mirror the Angular `FavoritesService` (`/api/v1/favorites/my`,
/// `/api/v1/favorites/unfollow`).
///
/// IMPORTANT (BR8.1): `unfollow` sends BOTH ids as percent-encoded QUERY
/// PARAMETERS with an EMPTY body — it does NOT use a JSON body, unlike
/// ``RosterService/cancelSale(championshipId:playerId:fallbackRejection:genericNetwork:)``.
/// This mirrors the Angular `FavoritesService.unfollow`
/// (`this.http.post(.../unfollow, {}, { params })`).
public protocol FavoritesService: Sendable {
    /// `GET /api/v1/favorites/my?championship_id=<id>` (W1 / FR1.1).
    func fetchFavorites(championshipId: String) async throws -> [FavoritePlayer]

    /// `POST /api/v1/favorites/unfollow?championship_id=<id>&player_id=<id>`
    /// with an EMPTY body and both ids as query parameters (W4 / FR5 / BR8.1).
    /// Maps the outcome to a ``MarketWriteOutcome`` using the supplied localized
    /// notices.
    func unfollow(
        championshipId: String,
        playerId: String,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome
}

/// `NetworkClient`-backed ``FavoritesService``.
public actor HTTPFavoritesService: FavoritesService {
    private let network: any NetworkClient

    public init(network: any NetworkClient) {
        self.network = network
    }

    public func fetchFavorites(championshipId: String) async throws -> [FavoritePlayer] {
        let request = APIRequest(
            method: .get,
            path: "/api/v1/favorites/my?championship_id=\(encode(championshipId))"
        )
        let result: Result<FavoritesResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            return response.players
        case .failure(let error):
            throw error
        }
    }

    public func unfollow(
        championshipId: String,
        playerId: String,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome {
        // Exact query contract (W4 / BR8.1), mirroring the Angular
        // `FavoritesService.unfollow`: championship_id + player_id as query
        // parameters, EMPTY body (no `body:` on the request — NOT a JSON body).
        let query = "championship_id=\(encode(championshipId))&player_id=\(encode(playerId))"
        let request = APIRequest(method: .post, path: "/api/v1/favorites/unfollow?\(query)")
        let result: Result<MarketWriteResponse, NetworkError> = await network.send(request)
        return MarketWriteOutcome.from(
            result: result,
            fallbackRejection: fallbackRejection,
            genericNetwork: genericNetwork
        )
    }

    /// Percent-encode a query value so an id with reserved characters cannot
    /// break the query string. Falls back to the raw value when the character
    /// set somehow rejects it (unreachable for ids).
    private func encode(_ value: String) -> String {
        value.addingPercentEncoding(withAllowedCharacters: .favoritesQueryValueAllowed) ?? value
    }
}

extension CharacterSet {
    /// Characters allowed in a single URL query VALUE: the standard query set
    /// minus the delimiters `&`, `=`, `+`, and `?` that would otherwise be read
    /// as structure. (Named distinctly from the Market/Roster helpers to avoid
    /// a redeclaration across files.)
    fileprivate static let favoritesQueryValueAllowed: CharacterSet = {
        var set = CharacterSet.urlQueryAllowed
        set.remove(charactersIn: "&=+?")
        return set
    }()
}
