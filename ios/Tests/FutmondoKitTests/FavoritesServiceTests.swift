import XCTest
@testable import FutmondoKit

/// In-memory `NetworkClient` double for the favourites service. Like
/// `FakeMarketNetworkClient` it scripts an outcome per path prefix and records
/// the full paths, but it ALSO records whether each request carried a body, so
/// the unfollow test can assert the BR8.1 contract: both ids in the query and
/// an EMPTY body (no JSON body). NO network, NO real credentials.
final class FakeFavoritesNetworkClient: NetworkClient, @unchecked Sendable {
    enum Outcome {
        case json(String)
        case failure(NetworkError)
    }

    private let lock = NSLock()
    private var handlers: [(prefix: String, outcome: Outcome)] = []
    private(set) var requestedPaths: [String] = []
    private(set) var hadBody: [Bool] = []

    private func withLock<R>(_ body: () -> R) -> R {
        lock.lock(); defer { lock.unlock() }
        return body()
    }

    func setOutcome(pathPrefix prefix: String, _ outcome: Outcome) {
        withLock { handlers.append((prefix, outcome)) }
    }

    func lastPath() -> String? { withLock { requestedPaths.last } }
    func lastHadBody() -> Bool? { withLock { hadBody.last } }

    func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError> {
        let outcome: Outcome? = withLock {
            requestedPaths.append(request.path)
            hadBody.append(request.body != nil)
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

final class FavoritesServiceTests: XCTestCase {
    private let myPrefix = "/api/v1/favorites/my"
    private let unfollowPrefix = "/api/v1/favorites/unfollow"
    private let fallback = "No se pudo quitar de favoritos."
    private let generic = "Error de conexión. Inténtalo de nuevo."

    private let okFavorites = #"""
    [
      { "player_id": "p-1", "name": "N", "slug": "s", "team": "T",
        "value": 1000000, "rating": 6.9, "sofascore_rating": 7.5,
        "home_average": 7.1, "away_average": 6.2, "matches": 18 }
    ]
    """#

    // MARK: - 1. fetchFavorites builds the EXACT backend endpoint (C1 / BR8.1)

    func testFetchFavoritesEndpointAndDecode() async throws {
        let net = FakeFavoritesNetworkClient()
        net.setOutcome(pathPrefix: myPrefix, .json(okFavorites))
        let service = HTTPFavoritesService(network: net)

        let favorites = try await service.fetchFavorites(championshipId: "champ-1")
        XCTAssertEqual(favorites.count, 1)
        XCTAssertEqual(favorites.first?.sofascoreRating, 7.5)
        XCTAssertEqual(
            net.lastPath(),
            "/api/v1/favorites/my?championship_id=champ-1",
            "exact W1 query contract"
        )
        XCTAssertEqual(net.lastHadBody(), false, "a GET carries no body")
    }

    // MARK: - 2. fetchFavorites tolerates the wrapped shape

    func testFetchFavoritesWrappedShape() async throws {
        let net = FakeFavoritesNetworkClient()
        net.setOutcome(
            pathPrefix: myPrefix,
            .json(#"{ "favorites": [ { "player_id": "z", "name": "Z", "slug": "z", "team": "T", "value": 5 } ] }"#)
        )
        let service = HTTPFavoritesService(network: net)
        let favorites = try await service.fetchFavorites(championshipId: "c")
        XCTAssertEqual(favorites.map(\.playerId), ["z"])
    }

    // MARK: - 3. fetchFavorites error propagates as typed NetworkError, no id leak

    func testFetchFavoritesErrorPropagatesWithoutLeak() async {
        let net = FakeFavoritesNetworkClient()
        net.setOutcome(pathPrefix: myPrefix, .failure(.server(503)))
        let service = HTTPFavoritesService(network: net)
        let secret = "secret-champ-id-123"
        do {
            _ = try await service.fetchFavorites(championshipId: secret)
            XCTFail("Expected throw")
        } catch let error as NetworkError {
            XCTAssertEqual(error, .server(503))
            XCTAssertFalse("\(error)".contains(secret))
        } catch {
            XCTFail("Expected NetworkError")
        }
    }

    // MARK: - 4. unfollow builds QUERY PARAMS + EMPTY body and maps 2xx-true → .accepted (BR8.1)

    func testUnfollowAcceptedQueryParamsAndEmptyBody() async {
        let net = FakeFavoritesNetworkClient()
        net.setOutcome(pathPrefix: unfollowPrefix, .json(#"{"success": true}"#))
        let service = HTTPFavoritesService(network: net)

        let result = await service.unfollow(
            championshipId: "champ-1", playerId: "p-1",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(result, .accepted)
        XCTAssertEqual(
            net.lastPath(),
            "/api/v1/favorites/unfollow?championship_id=champ-1&player_id=p-1",
            "BR8.1: both ids as query params (NOT a JSON body)"
        )
        XCTAssertEqual(
            net.lastHadBody(), false,
            "BR8.1 regression: unfollow sends an EMPTY body, unlike cancelSale"
        )
    }

    // MARK: - 5. unfollow percent-encodes reserved characters in ids

    func testUnfollowPercentEncodesIds() async {
        let net = FakeFavoritesNetworkClient()
        net.setOutcome(pathPrefix: unfollowPrefix, .json(#"{"success": true}"#))
        let service = HTTPFavoritesService(network: net)
        _ = await service.unfollow(
            championshipId: "a b", playerId: "x&y",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(
            net.lastPath(),
            "/api/v1/favorites/unfollow?championship_id=a%20b&player_id=x%26y",
            "reserved query characters are percent-encoded"
        )
    }

    // MARK: - 6. unfollow 2xx-false → .rejected(message); 4xx → .rejected(fallback)

    func testUnfollowRejectedPaths() async {
        let net = FakeFavoritesNetworkClient()
        net.setOutcome(pathPrefix: unfollowPrefix, .json(#"{"success": false, "detail": "No es favorito"}"#))
        let service = HTTPFavoritesService(network: net)
        let rejected = await service.unfollow(
            championshipId: "c", playerId: "p",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(rejected, .rejected(message: "No es favorito"))

        let net2 = FakeFavoritesNetworkClient()
        net2.setOutcome(pathPrefix: unfollowPrefix, .failure(.clientError(400)))
        let service2 = HTTPFavoritesService(network: net2)
        let rejected2 = await service2.unfollow(
            championshipId: "c", playerId: "p",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(rejected2, .rejected(message: fallback))
    }

    // MARK: - 7. unfollow 5xx / transport → .networkError (list stays intact — BR5.4)

    func testUnfollowNetworkError() async {
        let net = FakeFavoritesNetworkClient()
        net.setOutcome(pathPrefix: unfollowPrefix, .failure(.server(500)))
        let service = HTTPFavoritesService(network: net)
        let result = await service.unfollow(
            championshipId: "c", playerId: "p",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(result, .networkError)

        let net2 = FakeFavoritesNetworkClient()
        net2.setOutcome(pathPrefix: unfollowPrefix, .failure(.transport("offline")))
        let service2 = HTTPFavoritesService(network: net2)
        let result2 = await service2.unfollow(
            championshipId: "c", playerId: "p",
            fallbackRejection: fallback, genericNetwork: generic
        )
        XCTAssertEqual(result2, .networkError)
    }
}
