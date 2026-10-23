import Foundation

/// Fetches the user's roster and on-sale list and performs sell / cancel-sale
/// writes (FR1.1 / FR8 / FR9 / C1). An `actor` so concurrent calls are
/// serialized on its executor; it owns no mutable state beyond the injected
/// transport.
///
/// Consumes the F1 ``NetworkClient`` (Bearer injected by the transport, SEC /
/// NFR3); it adds no dependency and never logs or embeds credentials in
/// errors. The backend contract is INMUTABLE (C1): the exact paths mirror the
/// Angular `RosterService` (`/api/v1/roster/my`, `/on-sale`, `/sell`,
/// `/cancel-sale`). `sell` returns the dedicated ``SellOutcome`` (which carries
/// `sold`/`total`); `cancelSale` reuses ``MarketWriteOutcome``.
public protocol RosterService: Sendable {
    /// `GET /api/v1/roster/my?championship_id=<id>` (W1 / FR1.1).
    func fetchRoster(championshipId: String) async throws -> [RosterPlayer]

    /// `GET /api/v1/roster/on-sale?championship_id=<id>` (W1 / FR1.1).
    func fetchOnSale(championshipId: String) async throws -> [OnSalePlayer]

    /// `POST /api/v1/roster/sell` with body `{ championship_id, player_ids }`
    /// (W5 / FR8). Maps the outcome to a ``SellOutcome`` using the supplied
    /// localized generic-network notice.
    func sell(
        championshipId: String,
        playerIds: [String],
        genericNetwork: String
    ) async -> SellOutcome

    /// `POST /api/v1/roster/cancel-sale` with body `{ championship_id,
    /// player_id }` (W6 / FR9). Maps the outcome to a ``MarketWriteOutcome``.
    func cancelSale(
        championshipId: String,
        playerId: String,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome
}

/// `NetworkClient`-backed ``RosterService``.
public actor HTTPRosterService: RosterService {
    private let network: any NetworkClient

    public init(network: any NetworkClient) {
        self.network = network
    }

    public func fetchRoster(championshipId: String) async throws -> [RosterPlayer] {
        let request = APIRequest(
            method: .get,
            path: "/api/v1/roster/my?championship_id=\(encode(championshipId))"
        )
        let result: Result<RosterResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            return response.players
        case .failure(let error):
            throw error
        }
    }

    public func fetchOnSale(championshipId: String) async throws -> [OnSalePlayer] {
        let request = APIRequest(
            method: .get,
            path: "/api/v1/roster/on-sale?championship_id=\(encode(championshipId))"
        )
        let result: Result<OnSaleResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            return response.players
        case .failure(let error):
            throw error
        }
    }

    public func sell(
        championshipId: String,
        playerIds: [String],
        genericNetwork: String
    ) async -> SellOutcome {
        // Exact body contract (W5), mirroring the Angular `RosterService.sell`:
        // { championship_id, player_ids }.
        let body = SellRequestBody(championshipId: championshipId, playerIds: playerIds)
        let request = APIRequest(
            method: .post,
            path: "/api/v1/roster/sell",
            body: AnyEncodable(body)
        )
        let result: Result<SellResponse, NetworkError> = await network.send(request)
        return SellOutcome.from(result: result, genericNetwork: genericNetwork)
    }

    public func cancelSale(
        championshipId: String,
        playerId: String,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome {
        // Exact body contract (W6), mirroring the Angular
        // `RosterService.cancelSale`: { championship_id, player_id }.
        let body = CancelSaleRequestBody(championshipId: championshipId, playerId: playerId)
        let request = APIRequest(
            method: .post,
            path: "/api/v1/roster/cancel-sale",
            body: AnyEncodable(body)
        )
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
        value.addingPercentEncoding(withAllowedCharacters: .rosterQueryValueAllowed) ?? value
    }
}

/// JSON body of `POST /api/v1/roster/sell` (snake_case wire keys).
private struct SellRequestBody: Encodable {
    let championshipId: String
    let playerIds: [String]

    private enum CodingKeys: String, CodingKey {
        case championshipId = "championship_id"
        case playerIds = "player_ids"
    }
}

/// JSON body of `POST /api/v1/roster/cancel-sale` (snake_case wire keys).
private struct CancelSaleRequestBody: Encodable {
    let championshipId: String
    let playerId: String

    private enum CodingKeys: String, CodingKey {
        case championshipId = "championship_id"
        case playerId = "player_id"
    }
}

extension CharacterSet {
    /// Characters allowed in a single URL query VALUE: the standard query set
    /// minus the delimiters `&`, `=`, `+`, and `?` that would otherwise be read
    /// as structure. (Named distinctly from the Market helper to avoid a
    /// redeclaration across files.)
    fileprivate static let rosterQueryValueAllowed: CharacterSet = {
        var set = CharacterSet.urlQueryAllowed
        set.remove(charactersIn: "&=+?")
        return set
    }()
}
