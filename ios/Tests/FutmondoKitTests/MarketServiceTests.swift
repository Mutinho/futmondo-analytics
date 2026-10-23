import XCTest
@testable import FutmondoKit

/// In-memory `NetworkClient` double for the market services. Scripts an outcome
/// per path prefix and records the full paths requested, so tests can assert
/// both the decoded value and the exact query string. Mirrors the F2
/// `FakeBudgetNetworkClient` pattern. NO network, NO real credentials.
final class FakeMarketNetworkClient: NetworkClient, @unchecked Sendable {
    enum Outcome {
        case json(String)
        case failure(NetworkError)
    }

    private let lock = NSLock()
    private var handlers: [(prefix: String, outcome: Outcome)] = []
    private(set) var requestedPaths: [String] = []

    private func withLock<R>(_ body: () -> R) -> R {
        lock.lock(); defer { lock.unlock() }
        return body()
    }

    /// Register an outcome for requests whose path has `prefix`. Longer
    /// prefixes should be registered first so a more specific route wins.
    func setOutcome(pathPrefix prefix: String, _ outcome: Outcome) {
        withLock { handlers.append((prefix, outcome)) }
    }

    func lastPath() -> String? { withLock { requestedPaths.last } }

    func requestCount(forPrefix prefix: String) -> Int {
        withLock { requestedPaths.filter { $0.hasPrefix(prefix) }.count }
    }

    func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError> {
        let outcome: Outcome? = withLock {
            requestedPaths.append(request.path)
            return handlers.first { request.path.hasPrefix($0.prefix) }?.outcome
        }
        guard let outcome else { return .failure(.unexpectedStatus(0)) }
        switch outcome {
        case .json(let body):
            let data = body.data(using: .utf8) ?? Data()
            do {
                return .success(try JSONDecoder().decode(T.self, from: data))
            } catch {
                return .failure(.decoding(error.localizedDescription))
            }
        case .failure(let error):
            return .failure(error)
        }
    }
}

final class MarketServiceTests: XCTestCase {
    private let todayPrefix = "/api/v1/market/today"
    private let bidPrefix = "/api/v1/market/bid"
    private let cancelPrefix = "/api/v1/market/cancelbid"
    private let fallback = "No se pudo registrar la operación."
    private let generic = "Error de red. Inténtalo de nuevo."

    private let okToday = #"""
    {
      "success": true,
      "players": [
        { "player_id": "p-1", "slug": "s", "name": "N", "team": "T",
          "value": 1000000, "market_price": 500000, "suggested_bid": 600000,
          "is_favorite": false }
      ],
      "user_info": { "balance": 10000000, "team_value": 0, "max_bid": 20000000,
        "active_bids_total": 3000000, "available_for_bids": 17000000 }
    }
    """#

    // MARK: - 1. loadToday OK decodes the page

    func testLoadTodaySuccess() async throws {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: todayPrefix, .json(okToday))
        let service = HTTPMarketService(network: net)

        let response = try await service.loadToday(championshipId: "champ-1")
        XCTAssertEqual(response.players.count, 1)
        XCTAssertEqual(response.userInfo.availableForBids, 17_000_000)
        XCTAssertEqual(net.lastPath(), "/api/v1/market/today?championship_id=champ-1")
    }

    // MARK: - 2. loadToday empty page → empty players, no throw

    func testLoadTodayEmpty() async throws {
        let empty = #"""
        { "success": true, "players": [],
          "user_info": { "balance": 0, "team_value": 0, "max_bid": 0,
            "active_bids_total": 0, "available_for_bids": 0 } }
        """#
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: todayPrefix, .json(empty))
        let service = HTTPMarketService(network: net)

        let response = try await service.loadToday(championshipId: "champ-1")
        XCTAssertTrue(response.players.isEmpty)
    }

    // MARK: - 3. loadToday error propagates as typed NetworkError, no id leak

    func testLoadTodayErrorPropagatesWithoutLeak() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: todayPrefix, .failure(.server(503)))
        let service = HTTPMarketService(network: net)
        let secret = "secret-champ-id-123"
        do {
            _ = try await service.loadToday(championshipId: secret)
            XCTFail("Expected throw")
        } catch let error as NetworkError {
            XCTAssertEqual(error, .server(503))
            XCTAssertFalse("\(error)".contains(secret))
        } catch {
            XCTFail("Expected NetworkError")
        }
    }

    // MARK: - 4. placeBid builds the exact query and maps 2xx-true → .accepted

    func testPlaceBidAcceptedAndQuery() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: bidPrefix, .json(#"{"success": true}"#))
        let service = HTTPMarketService(network: net)

        let result = await service.placeBid(
            championshipId: "champ-1", playerId: "p-1", playerSlug: "vini",
            price: 650000, fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(result, .accepted)
        XCTAssertEqual(
            net.lastPath(),
            "/api/v1/market/bid?championship_id=champ-1&player_id=p-1&player_slug=vini&price=650000&is_clause=false",
            "exact W4 query contract incl. is_clause=false"
        )
    }

    // MARK: - 5. placeBid 2xx-false → .rejected(message); 422 → .rejected(fallback)

    func testPlaceBidRejectedPaths() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: bidPrefix, .json(#"{"success": false, "detail": "Puja baja"}"#))
        let service = HTTPMarketService(network: net)
        let rejected = await service.placeBid(
            championshipId: "c", playerId: "p", playerSlug: "s", price: 1,
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(rejected, .rejected(message: "Puja baja"))

        let net2 = FakeMarketNetworkClient()
        net2.setOutcome(pathPrefix: bidPrefix, .failure(.clientError(422)))
        let service2 = HTTPMarketService(network: net2)
        let rejected2 = await service2.placeBid(
            championshipId: "c", playerId: "p", playerSlug: "s", price: 1,
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(rejected2, .rejected(message: fallback))
    }

    // MARK: - 6. placeBid 5xx → .networkError

    func testPlaceBidNetworkError() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: bidPrefix, .failure(.server(500)))
        let service = HTTPMarketService(network: net)
        let result = await service.placeBid(
            championshipId: "c", playerId: "p", playerSlug: "s", price: 1,
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(result, .networkError)
    }

    // MARK: - 7. cancelBid builds the exact query and maps 2xx-true → .accepted

    func testCancelBidAcceptedAndQuery() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: cancelPrefix, .json(#"{"success": true}"#))
        let service = HTTPMarketService(network: net)
        let result = await service.cancelBid(
            championshipId: "champ-1", bidId: "bid-42",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(result, .accepted)
        XCTAssertEqual(
            net.lastPath(),
            "/api/v1/market/cancelbid?championship_id=champ-1&bid_id=bid-42",
            "exact W5 query contract"
        )
    }

    // MARK: - 8. cancelBid transport failure → .networkError

    func testCancelBidTransportError() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: cancelPrefix, .failure(.transport("offline")))
        let service = HTTPMarketService(network: net)
        let result = await service.cancelBid(
            championshipId: "c", bidId: "b",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(result, .networkError)
    }
}

final class SofascoreServiceTests: XCTestCase {
    private let prefix = "/api/v1/sofascore/player/"

    private let okDetail = #"""
    { "success": true, "player": { "player_name": "Vinicius", "rating": 7.8, "goals": 12, "starter_pct": 95 } }
    """#

    // MARK: - 1. loadDetail OK → .loaded with decoded stats (unwrapped from `player`)

    func testLoadDetailLoaded() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .json(okDetail))
        let service = HTTPSofascoreService(network: net)
        let outcome = await service.loadDetail(playerName: "Vinicius", championshipId: "champ-1")
        guard case .loaded(let detail) = outcome else {
            return XCTFail("Expected .loaded, got \(outcome)")
        }
        XCTAssertEqual(detail.playerName, "Vinicius")
        XCTAssertEqual(detail.rating, 7.8)
        XCTAssertEqual(detail.goals, 12)
        XCTAssertEqual(detail.starterPct, 95)
    }

    /// A 2xx body with `success:false` and no `player` is "sin datos" (.empty),
    /// not a hard error.
    func testLoadDetailSuccessFalseIsEmpty() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .json(#"{ "success": false }"#))
        let service = HTTPSofascoreService(network: net)
        let outcome = await service.loadDetail(playerName: "Nadie", championshipId: "c")
        XCTAssertEqual(outcome, .empty)
    }

    // MARK: - 2. 404 → .empty (sin datos), not an error (W7)

    func testLoadDetail404IsEmpty() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .failure(.clientError(404)))
        let service = HTTPSofascoreService(network: net)
        let outcome = await service.loadDetail(playerName: "Nobody", championshipId: "c")
        XCTAssertEqual(outcome, .empty)
    }

    // MARK: - 3. 5xx → .failed

    func testLoadDetailServerErrorIsFailed() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .failure(.server(502)))
        let service = HTTPSofascoreService(network: net)
        let outcome = await service.loadDetail(playerName: "X", championshipId: "c")
        XCTAssertEqual(outcome, .failed)
    }

    // MARK: - 4. transport failure → .failed

    func testLoadDetailTransportIsFailed() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .failure(.transport("offline")))
        let service = HTTPSofascoreService(network: net)
        let outcome = await service.loadDetail(playerName: "X", championshipId: "c")
        XCTAssertEqual(outcome, .failed)
    }

    // MARK: - 5. other 4xx (not 404) → .failed

    func testLoadDetailOther4xxIsFailed() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .failure(.clientError(403)))
        let service = HTTPSofascoreService(network: net)
        let outcome = await service.loadDetail(playerName: "X", championshipId: "c")
        XCTAssertEqual(outcome, .failed)
    }

    // MARK: - 6. decode failure → .failed

    func testLoadDetailDecodeFailureIsFailed() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .json(#"{ "unexpected": true }"#))
        let service = HTTPSofascoreService(network: net)
        let outcome = await service.loadDetail(playerName: "X", championshipId: "c")
        XCTAssertEqual(outcome, .failed)
    }

    // MARK: - 7. player name is percent-encoded into the path segment

    func testLoadDetailEncodesPlayerNameAndQuery() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: "/api/v1/sofascore/player/", .json(okDetail))
        let service = HTTPSofascoreService(network: net)
        _ = await service.loadDetail(playerName: "Luka Modric", championshipId: "champ-1")
        XCTAssertEqual(
            net.lastPath(),
            "/api/v1/sofascore/player/Luka%20Modric?championship_id=champ-1",
            "space in the name is encoded in the path segment"
        )
    }

    // MARK: - 8. a detail failure returns a typed outcome, never leaks the name

    func testLoadDetailOutcomeNeverLeaksName() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: prefix, .failure(.server(500)))
        let service = HTTPSofascoreService(network: net)
        let secret = "ultra-secret-player"
        let outcome = await service.loadDetail(playerName: secret, championshipId: "c")
        // The outcome is a bare enum case with no associated name payload.
        XCTAssertEqual(outcome, .failed)
        XCTAssertFalse("\(outcome)".contains(secret))
    }
}
