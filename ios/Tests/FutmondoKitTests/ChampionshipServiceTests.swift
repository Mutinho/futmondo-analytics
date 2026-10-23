import XCTest
@testable import FutmondoKit

/// Reuses `FakeBudgetNetworkClient` (defined in `BudgetServiceTests.swift`).
/// The primary path `/api/v1/user/championships` and the fallback
/// `/api/v1/championships` share the `/api/v1/championships` suffix, so the
/// fake matches on the exact distinguishing prefixes below.
final class ChampionshipServiceTests: XCTestCase {
    private let primaryPath = "/api/v1/user/championships"
    private let fallbackPath = "/api/v1/championships"

    private func body(_ id: String, name: String) -> String {
        #"""
        { "success": true, "championships": [
          { "championship_id": "\#(id)", "name": "\#(name)",
            "initial_budget": 100000000, "has_clauses": false,
            "excluded_teams": [] } ] }
        """#
    }

    /// Fake that routes by EXACT path (primary vs fallback), since the fallback
    /// path is a prefix of the primary one.
    private final class ExactPathFake: NetworkClient, @unchecked Sendable {
        enum Outcome { case json(String); case failure(NetworkError) }
        private let lock = NSLock()
        private var handlers: [String: Outcome] = [:]
        private(set) var order: [String] = []

        private func withLock<R>(_ body: () -> R) -> R {
            lock.lock(); defer { lock.unlock() }
            return body()
        }

        func set(_ path: String, _ outcome: Outcome) {
            withLock { handlers[path] = outcome }
        }
        func calls() -> [String] { withLock { order } }

        func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError> {
            let outcome: Outcome? = withLock {
                order.append(request.path)
                return handlers[request.path]
            }
            guard let outcome else { return .failure(.unexpectedStatus(0)) }
            switch outcome {
            case .json(let b):
                let data = b.data(using: .utf8) ?? Data()
                do { return .success(try JSONDecoder().decode(T.self, from: data)) }
                catch { return .failure(.decoding(error.localizedDescription)) }
            case .failure(let e):
                return .failure(e)
            }
        }
    }

    // MARK: - 1. Primary OK → returns list, no fallback call

    func testPrimarySuccessReturnsListWithoutFallback() async throws {
        let net = ExactPathFake()
        net.set(primaryPath, .json(body("c-primary", name: "Primary League")))
        let service = HTTPChampionshipService(network: net)

        let list = try await service.fetchChampionships()

        XCTAssertEqual(list.map(\.championshipId), ["c-primary"])
        XCTAssertEqual(net.calls(), [primaryPath], "fallback must not be called on primary success")
    }

    // MARK: - 2. Primary network-throw → fallback used

    func testPrimaryNetworkErrorFallsBackToSecondary() async throws {
        let net = ExactPathFake()
        net.set(primaryPath, .failure(.server(500)))
        net.set(fallbackPath, .json(body("c-fallback", name: "Fallback League")))
        let service = HTTPChampionshipService(network: net)

        let list = try await service.fetchChampionships()

        XCTAssertEqual(list.map(\.championshipId), ["c-fallback"])
        XCTAssertEqual(net.calls(), [primaryPath, fallbackPath], "fallback used after primary throw")
    }

    // MARK: - 3. Primary decode-throw → fallback used

    func testPrimaryDecodeErrorFallsBackToSecondary() async throws {
        let net = ExactPathFake()
        net.set(primaryPath, .json(#"{"unexpected": true}"#))  // decode failure
        net.set(fallbackPath, .json(body("c-fallback-2", name: "Fallback Two")))
        let service = HTTPChampionshipService(network: net)

        let list = try await service.fetchChampionships()

        XCTAssertEqual(list.map(\.championshipId), ["c-fallback-2"])
        XCTAssertEqual(net.calls(), [primaryPath, fallbackPath])
    }

    // MARK: - 4. Both throw → fallback's error propagates

    func testBothFailPropagatesFallbackError() async {
        let net = ExactPathFake()
        net.set(primaryPath, .failure(.server(500)))
        net.set(fallbackPath, .failure(.forbidden))
        let service = HTTPChampionshipService(network: net)

        do {
            _ = try await service.fetchChampionships()
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            XCTAssertEqual(error, .forbidden, "the FALLBACK's error must propagate, not the primary's")
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }

    // MARK: - 5. Both throw with decode primary → fallback's error propagates, no leak

    func testBothFailFromDecodePrimaryPropagatesFallbackErrorNoLeak() async {
        let net = ExactPathFake()
        net.set(primaryPath, .json(#"{"bad":1}"#))          // decode-throw
        net.set(fallbackPath, .failure(.transport("offline")))
        let service = HTTPChampionshipService(network: net)

        do {
            _ = try await service.fetchChampionships()
            XCTFail("Expected a thrown error")
        } catch let error as NetworkError {
            guard case .transport(let message) = error else {
                return XCTFail("Expected fallback .transport, got \(error)")
            }
            XCTAssertEqual(message, "offline")
            // No credential/token material in the surfaced message.
            XCTAssertFalse(message.lowercased().contains("bearer"))
            XCTAssertFalse(message.lowercased().contains("token"))
        } catch {
            XCTFail("Expected NetworkError, got \(error)")
        }
    }

    // MARK: - 6. Empty championships list decodes to empty

    func testEmptyChampionshipsList() async throws {
        let net = ExactPathFake()
        net.set(primaryPath, .json(#"{ "success": true, "championships": [] }"#))
        let service = HTTPChampionshipService(network: net)

        let list = try await service.fetchChampionships()
        XCTAssertTrue(list.isEmpty)
    }
}
