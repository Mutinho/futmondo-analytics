import Foundation

/// Fetches the market page and performs bid / cancel-bid writes (FR2 / FR6 /
/// FR7 / C5). An `actor` so concurrent calls are serialized on its executor;
/// it owns no mutable state beyond the injected transport.
///
/// Consumes the F1 `NetworkClient` (Bearer injected by the transport, SEC /
/// NFR3); it adds no dependency and never logs or embeds credentials in
/// errors. The `price`/ids travel as query parameters on the path; the typed
/// `NetworkError` never echoes the full URL, so a failed call cannot leak them.
public protocol MarketService: Sendable {
    /// `GET /api/v1/market/today?championship_id=<id>` (W1).
    func loadToday(championshipId: String) async throws -> MarketTodayResponse

    /// `POST /api/v1/market/bid` with the exact query parameters (W4). Maps the
    /// outcome to a ``MarketWriteOutcome`` using the supplied localized notices.
    func placeBid(
        championshipId: String,
        playerId: String,
        playerSlug: String,
        price: Int,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome

    /// `POST /api/v1/market/cancelbid` with the exact query parameters (W5).
    func cancelBid(
        championshipId: String,
        bidId: String,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome
}

/// `NetworkClient`-backed ``MarketService``.
public actor HTTPMarketService: MarketService {
    private let network: any NetworkClient

    public init(network: any NetworkClient) {
        self.network = network
    }

    public func loadToday(championshipId: String) async throws -> MarketTodayResponse {
        let request = APIRequest(
            method: .get,
            path: "/api/v1/market/today?championship_id=\(encode(championshipId))"
        )
        let result: Result<MarketTodayResponse, NetworkError> = await network.send(request)
        switch result {
        case .success(let response):
            return response
        case .failure(let error):
            throw error
        }
    }

    public func placeBid(
        championshipId: String,
        playerId: String,
        playerSlug: String,
        price: Int,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome {
        // Exact query contract (W4): championship_id, player_id, player_slug,
        // price, is_clause=false.
        let query = "championship_id=\(encode(championshipId))"
            + "&player_id=\(encode(playerId))"
            + "&player_slug=\(encode(playerSlug))"
            + "&price=\(price)"
            + "&is_clause=false"
        let request = APIRequest(method: .post, path: "/api/v1/market/bid?\(query)")
        let result: Result<MarketWriteResponse, NetworkError> = await network.send(request)
        return MarketWriteOutcome.from(
            result: result,
            fallbackRejection: fallbackRejection,
            genericNetwork: genericNetwork
        )
    }

    public func cancelBid(
        championshipId: String,
        bidId: String,
        fallbackRejection: String,
        genericNetwork: String
    ) async -> MarketWriteOutcome {
        // Exact query contract (W5): championship_id, bid_id.
        let query = "championship_id=\(encode(championshipId))&bid_id=\(encode(bidId))"
        let request = APIRequest(method: .post, path: "/api/v1/market/cancelbid?\(query)")
        let result: Result<MarketWriteResponse, NetworkError> = await network.send(request)
        return MarketWriteOutcome.from(
            result: result,
            fallbackRejection: fallbackRejection,
            genericNetwork: genericNetwork
        )
    }

    /// Percent-encode a query value so an id/slug with reserved characters
    /// cannot break the query string. Falls back to the raw value when the
    /// character set somehow rejects it (unreachable for ids/slugs).
    private func encode(_ value: String) -> String {
        value.addingPercentEncoding(withAllowedCharacters: .urlQueryValueAllowed) ?? value
    }
}

extension CharacterSet {
    /// Characters allowed in a single URL query VALUE: the standard query set
    /// minus the delimiters `&`, `=`, `+`, and `?` that would otherwise be read
    /// as structure.
    fileprivate static let urlQueryValueAllowed: CharacterSet = {
        var set = CharacterSet.urlQueryAllowed
        set.remove(charactersIn: "&=+?")
        return set
    }()
}
