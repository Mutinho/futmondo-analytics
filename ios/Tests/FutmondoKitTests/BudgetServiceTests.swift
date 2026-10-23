import XCTest
@testable import FutmondoKit

/// In-memory `NetworkClient` double for the Budget services. Scripts an outcome
/// per path and records the paths it was asked for, so tests can assert both
/// the decoded value and the fallback ordering. Mirrors the F1 fake pattern
/// (`SpyNetworkClient` in `AuthServiceTests`), matching on the path prefix so a
/// query string on the balances path still routes.
final class FakeBudgetNetworkClient: NetworkClient, @unchecked Sendable {
    enum Outcome {
        /// Raw JSON the client decodes into `T` (can produce a DecodingError).
        case json(String)
        /// A typed network failure.
        case failure(NetworkError)
    }

    private let lock = NSLock()
    private var handlers: [String: Outcome] = [:]
    private(set) var requestedPaths: [String] = []

    /// Scoped, synchronous locking — safe to call from an async context because
    /// the lock is never held across an `await` (Swift 6 async-safety).
    private func withLock<R>(_ body: () -> R) -> R {
        lock.lock(); defer { lock.unlock() }
        return body()
    }

    /// Register an outcome for requests whose path has `prefix`.
    func setOutcome(pathPrefix prefix: String, _ outcome: Outcome) {
        withLock { handlers[prefix] = outcome }
    }

    func requestCount(forPrefix prefix: String) -> Int {
        withLock { requestedPaths.filter { $0.hasPrefix(prefix) }.count }
    }

    func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError> {
        let outcome: Outcome? = withLock {
            requestedPaths.append(request.path)
            return handlers.first { request.path.hasPrefix($0.key) }?.value
        }

        guard let outcome else {
            return .failure(.unexpectedStatus(0))
        }
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

final class BudgetServiceTests: XCTestCase {
    private let balancesPrefix = "/api/v1/analytics/balances"

    private let okBalances = #"""
    {
      "success": true,
      "championship_id": "champ-1",
      "initial_budget": 100000000,
      "teams": [
        {
          "team_id": "t-1", "team_name": "Alpha", "balance": 5000000,
          "initial_budget": 100000000, "total_spent": 10000000,
          "total_income": 2000000, "purchases_count": 2, "sales_count": 1,
          "team_value": 90000000, "performance": 1000000, "max_bid": 8000000,
          "prizes": 500000
        }
      ]
    }
    """#

    // MARK: - 1. OK → returns decoded BalancesResponse

    func testFetchBalancesSuccess() async throws {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: balancesPrefix, .json(okBalances))
        let service = HTTPBudgetService(network: net)

        let response = try await service.fetchBalances(championshipId: "champ-1")

        XCTAssertEqual(response.championshipId, "champ-1")
        XCTAssertEqual(response.teams.count, 1)
        XCTAssertEqual(response.teams[0].balance, 5_000_000)
    }

    // MARK: - 2. Network error propagates as typed NetworkError

    func testFetchBalancesPropagatesNetworkError() async {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: balancesPrefix, .failure(.server(503)))
        let service = HTTPBudgetService(network: net)

        do {
            _ = try await service.fetchBalances(championshipId: "champ-1")
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            XCTAssertEqual(error, .server(503))
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }

    // MARK: - 3. Decode error propagates as .decoding

    func testFetchBalancesDecodeErrorPropagates() async {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: balancesPrefix, .json(#"{"success": true}"#))  // malformed
        let service = HTTPBudgetService(network: net)

        do {
            _ = try await service.fetchBalances(championshipId: "champ-1")
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            guard case .decoding = error else {
                return XCTFail("Expected .decoding, got \(error)")
            }
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }

    // MARK: - 4. No credential/id leak on network error (SR1)

    func testFetchBalancesErrorDoesNotLeakChampionshipId() async {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: balancesPrefix, .failure(.unauthorized))
        let service = HTTPBudgetService(network: net)

        let secretId = "super-secret-championship-id-12345"
        do {
            _ = try await service.fetchBalances(championshipId: secretId)
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            // NetworkError is Equatable with Int/String payloads only; its
            // description must not contain the id or any token.
            XCTAssertFalse("\(error)".contains(secretId))
            XCTAssertEqual(error, .unauthorized)
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }

    // MARK: - 5. No leak on a decode error (SR4 branch of SR1)

    func testFetchBalancesDecodeErrorDoesNotLeakChampionshipId() async {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: balancesPrefix, .json(#"{"bad": true}"#))
        let service = HTTPBudgetService(network: net)

        let secretId = "leak-check-championship-id-xyz"
        do {
            _ = try await service.fetchBalances(championshipId: secretId)
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            guard case .decoding(let message) = error else {
                return XCTFail("Expected .decoding, got \(error)")
            }
            // A Foundation DecodingError describes the type/key path, never the
            // request's query. Assert the id does not appear.
            XCTAssertFalse(message.contains(secretId))
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }

    // MARK: - 6. fetchTeamDetail OK → decodes incl. optional from/to (FR6)

    private let teamDetailPrefix = "/api/v1/analytics/balances/"

    private let okTeamDetail = #"""
    {
      "success": true,
      "team_id": "t-1",
      "team_name": "Alpha",
      "balance": 5000000,
      "initial_budget": 100000000,
      "total_spent": 10000000,
      "total_income": 2000000,
      "purchases": [
        { "player_id": "p-1", "player_name": "Vini", "price": 20000000,
          "date": "2026-01-15", "from": "Computer" }
      ],
      "sales": [
        { "player_id": "p-2", "player_name": "Modric", "price": 8000000,
          "date": "2026-02-01", "to": "Computer" }
      ]
    }
    """#

    func testFetchTeamDetailSuccess() async throws {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: teamDetailPrefix, .json(okTeamDetail))
        let service = HTTPBudgetService(network: net)

        let response = try await service.fetchTeamDetail(
            teamId: "t-1",
            championshipId: "champ-1"
        )

        XCTAssertEqual(response.teamId, "t-1")
        XCTAssertEqual(response.teamName, "Alpha")
        XCTAssertEqual(response.purchases.count, 1)
        XCTAssertEqual(response.purchases[0].from, "Computer")
        XCTAssertNil(response.purchases[0].to)
        XCTAssertEqual(response.sales.count, 1)
        XCTAssertEqual(response.sales[0].to, "Computer")
        XCTAssertNil(response.sales[0].from)
        // The id lands on the path, not the balances-list path.
        XCTAssertEqual(net.requestCount(forPrefix: teamDetailPrefix + "t-1"), 1)
    }

    // MARK: - 7. fetchTeamDetail network error propagates as typed NetworkError

    func testFetchTeamDetailPropagatesNetworkError() async {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: teamDetailPrefix, .failure(.clientError(404)))
        let service = HTTPBudgetService(network: net)

        do {
            _ = try await service.fetchTeamDetail(teamId: "t-1", championshipId: "champ-1")
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            XCTAssertEqual(error, .clientError(404))
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }

    // MARK: - 8. fetchTeamDetail no credential/id leak on error (SR1)

    func testFetchTeamDetailErrorDoesNotLeakIds() async {
        let net = FakeBudgetNetworkClient()
        net.setOutcome(pathPrefix: teamDetailPrefix, .failure(.unauthorized))
        let service = HTTPBudgetService(network: net)

        let secretTeam = "super-secret-team-id-98765"
        let secretChamp = "super-secret-championship-id-12345"
        do {
            _ = try await service.fetchTeamDetail(
                teamId: secretTeam,
                championshipId: secretChamp
            )
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            XCTAssertFalse("\(error)".contains(secretTeam))
            XCTAssertFalse("\(error)".contains(secretChamp))
            XCTAssertEqual(error, .unauthorized)
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }
}
