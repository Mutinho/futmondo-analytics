import XCTest
import Foundation
@testable import FutmondoKit

/// Configurable `NetworkClient` double: scripts a response per path and counts
/// invocations so tests can assert coalescing (one refresh for N concurrent
/// callers). Thread-safe (`NSLock`) because `AuthService` is an actor.
final class SpyNetworkClient: NetworkClient, @unchecked Sendable {
    /// Outcome a handler produces: either a JSON body (decoded by the client)
    /// or a `NetworkError`.
    enum Outcome {
        case json(String)
        case empty
        case failure(NetworkError)
    }

    private let lock = NSLock()
    private var handlers: [String: () -> Outcome] = [:]
    private(set) var callCounts: [String: Int] = [:]
    /// Optional async delay (seconds) injected before producing an outcome,
    /// used to widen the window for the concurrent-coalescing test.
    var refreshDelayNanos: UInt64 = 0

    func setHandler(path: String, _ handler: @escaping () -> Outcome) {
        withLock { handlers[path] = handler }
    }

    func count(for path: String) -> Int {
        withLock { callCounts[path] ?? 0 }
    }

    /// Synchronously record the call and snapshot the handler + delay under the
    /// lock. Returns the values needed to produce the outcome without holding
    /// the lock across an `await` (Swift 6 async-safety).
    private func recordAndSnapshot(path: String) -> (handler: (() -> Outcome)?, delay: UInt64) {
        withLock {
            callCounts[path, default: 0] += 1
            return (handlers[path], refreshDelayNanos)
        }
    }

    private func withLock<R>(_ body: () -> R) -> R {
        lock.lock()
        defer { lock.unlock() }
        return body()
    }

    func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError> {
        let (handler, delay) = recordAndSnapshot(path: request.path)

        if delay > 0, request.path == "/auth/refresh" {
            try? await Task.sleep(nanoseconds: delay)
        }

        guard let handler else {
            return .failure(.unexpectedStatus(0))
        }

        switch handler() {
        case .json(let body):
            let data = body.data(using: .utf8) ?? Data()
            do {
                let value = try JSONDecoder().decode(T.self, from: data)
                return .success(value)
            } catch {
                return .failure(.decoding(error.localizedDescription))
            }
        case .empty:
            if let empty = EmptyResponse() as? T {
                return .success(empty)
            }
            return .failure(.decoding("empty for non-EmptyResponse"))
        case .failure(let error):
            return .failure(error)
        }
    }
}

final class AuthServiceTests: XCTestCase {
    private let loginBody = #"""
    {"access_token":"acc-1","refresh_token":"ref-1","token_type":"bearer","expires_in":3600,"user_id":"u-1","email":"javi@futmondo.test","display_name":"Javi"}
    """#

    private func makeService(
        network: SpyNetworkClient,
        keychain: InMemoryKeychainStore,
        holder: TokenHolder,
        flagStore: InMemoryLogoutFlagStore = InMemoryLogoutFlagStore()
    ) -> AuthService {
        AuthService(network: network, keychain: keychain, tokenHolder: holder, flagStore: flagStore)
    }

    // MARK: - Login OK

    func testLoginSuccessStoresAccessInMemoryHolderAndRefreshInKeychain() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/login") { .json(self.loginBody) }
        let keychain = InMemoryKeychainStore()
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        let result = await service.login(email: "javi@futmondo.test", password: "secret")

        switch result {
        case .success(let session):
            XCTAssertEqual(session.accessToken, "acc-1")
            XCTAssertEqual(session.user, UserMe(userId: "u-1", email: "javi@futmondo.test"))
        case .failure(let error):
            XCTFail("Expected success, got \(error)")
        }
        // Effect: access token in memory AND in the holder; refresh in Keychain.
        let inMemory = await service.currentAccessToken()
        XCTAssertEqual(inMemory, "acc-1")
        XCTAssertEqual(holder.get(), "acc-1")
        XCTAssertEqual(keychain.peekToken(), "ref-1")
    }

    // MARK: - Login 401

    func testLoginUnauthorizedMapsToInvalidCredentialsAndStoresNothing() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/login") { .failure(.unauthorized) }
        let keychain = InMemoryKeychainStore()
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        let result = await service.login(email: "javi@futmondo.test", password: "wrong")

        XCTAssertEqual(result, .failure(.invalidCredentials))
        let inMemory = await service.currentAccessToken()
        XCTAssertNil(inMemory)
        XCTAssertNil(holder.get())
        XCTAssertNil(keychain.peekToken())
    }

    // MARK: - Bootstrap: no token

    func testBootstrapNoTokenReturnsUnauthenticated() async {
        let network = SpyNetworkClient()
        let keychain = InMemoryKeychainStore(initialToken: nil)
        let service = makeService(network: network, keychain: keychain, holder: TokenHolder())

        let state = await service.bootstrap()

        XCTAssertEqual(state, .unauthenticated)
        XCTAssertEqual(network.count(for: "/auth/refresh"), 0)
    }

    // MARK: - Bootstrap: refresh 200 -> authenticated

    func testBootstrapWithValidTokenReturnsAuthenticated() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/refresh") { .json(#"{"access_token":"acc-boot","expires_in":3600}"#) }
        let keychain = InMemoryKeychainStore(initialToken: "ref-stored")
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        let state = await service.bootstrap()

        guard case .authenticated(let session) = state else {
            return XCTFail("Expected .authenticated, got \(state)")
        }
        XCTAssertEqual(session.accessToken, "acc-boot")
        XCTAssertEqual(holder.get(), "acc-boot")
        XCTAssertEqual(keychain.peekToken(), "ref-stored", "refresh token preserved")
    }

    // MARK: - Bootstrap: 401/revoked -> clears Keychain -> unauthenticated

    func testBootstrapRevokedTokenClearsKeychainAndReturnsUnauthenticated() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/refresh") { .failure(.unauthorized) }
        let keychain = InMemoryKeychainStore(initialToken: "ref-revoked")
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        let state = await service.bootstrap()

        XCTAssertEqual(state, .unauthenticated)
        XCTAssertNil(keychain.peekToken(), "revoked refresh token must be deleted")
        XCTAssertNil(holder.get())
    }

    // MARK: - Bootstrap: transport/5xx -> offlinePreserved (Keychain kept)

    func testBootstrapTransportErrorPreservesKeychainAndReturnsOffline() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/refresh") { .failure(.transport("offline")) }
        let keychain = InMemoryKeychainStore(initialToken: "ref-kept")
        let service = makeService(network: network, keychain: keychain, holder: TokenHolder())

        let state = await service.bootstrap()

        XCTAssertEqual(state, .offlinePreserved)
        XCTAssertEqual(keychain.peekToken(), "ref-kept", "token must be preserved for a later retry")
    }

    func testBootstrapServerErrorReturnsOfflinePreserved() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/refresh") { .failure(.server(503)) }
        let keychain = InMemoryKeychainStore(initialToken: "ref-kept")
        let service = makeService(network: network, keychain: keychain, holder: TokenHolder())

        let state = await service.bootstrap()

        XCTAssertEqual(state, .offlinePreserved)
        XCTAssertEqual(keychain.peekToken(), "ref-kept")
    }

    // MARK: - Refresh success mints a new access token

    func testRefreshSuccessMintsNewAccessToken() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/refresh") { .json(#"{"access_token":"acc-new","expires_in":3600}"#) }
        let keychain = InMemoryKeychainStore(initialToken: "ref-1")
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        let result = await service.refresh()

        XCTAssertEqual(result, .success("acc-new"))
        XCTAssertEqual(holder.get(), "acc-new")
        let inMemory = await service.currentAccessToken()
        XCTAssertEqual(inMemory, "acc-new")
    }

    // MARK: - Refresh 401 -> refreshFailed

    func testRefreshUnauthorizedMapsToRefreshFailed() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/refresh") { .failure(.unauthorized) }
        let keychain = InMemoryKeychainStore(initialToken: "ref-1")
        let service = makeService(network: network, keychain: keychain, holder: TokenHolder())

        let result = await service.refresh()

        XCTAssertEqual(result, .failure(.refreshFailed))
    }

    func testRefreshWithoutStoredTokenFails() async {
        let network = SpyNetworkClient()
        let keychain = InMemoryKeychainStore(initialToken: nil)
        let service = makeService(network: network, keychain: keychain, holder: TokenHolder())

        let result = await service.refresh()

        XCTAssertEqual(result, .failure(.refreshFailed))
        XCTAssertEqual(network.count(for: "/auth/refresh"), 0)
    }

    // MARK: - Coalescing: N concurrent refreshes -> 1 network call

    func testConcurrentRefreshesCoalesceIntoSingleNetworkCall() async {
        let network = SpyNetworkClient()
        network.refreshDelayNanos = 50_000_000 // 50ms window so both callers overlap
        network.setHandler(path: "/auth/refresh") { .json(#"{"access_token":"acc-coalesced","expires_in":3600}"#) }
        let keychain = InMemoryKeychainStore(initialToken: "ref-1")
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        async let first = service.refresh()
        async let second = service.refresh()
        let results = await [first, second]

        XCTAssertEqual(results[0], .success("acc-coalesced"))
        XCTAssertEqual(results[1], .success("acc-coalesced"))
        // Effect: both callers shared ONE refresh network call.
        XCTAssertEqual(network.count(for: "/auth/refresh"), 1, "coalescing must collapse to a single refresh")
        XCTAssertEqual(holder.get(), "acc-coalesced")
    }

    // MARK: - Logout OK: clears Keychain + holder + in-memory token

    func testLogoutSuccessClearsEverythingAndNoPendingRevocation() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/login") { .json(self.loginBody) }
        network.setHandler(path: "/auth/logout") { .empty }
        let keychain = InMemoryKeychainStore()
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        _ = await service.login(email: "javi@futmondo.test", password: "secret")
        await service.logout()

        let inMemory = await service.currentAccessToken()
        XCTAssertNil(inMemory, "in-memory access token cleared")
        XCTAssertNil(holder.get(), "holder snapshot cleared")
        XCTAssertNil(keychain.peekToken(), "refresh token deleted from Keychain")
        let pending = await service.pendingLogoutRevocation
        XCTAssertFalse(pending, "no pending revocation on a successful logout")
    }

    // MARK: - Logout with network down: local state cleared + pending flag set

    func testLogoutNetworkFailureClearsLocalStateAndSetsPendingRevocation() async {
        let network = SpyNetworkClient()
        network.setHandler(path: "/auth/login") { .json(self.loginBody) }
        network.setHandler(path: "/auth/logout") { .failure(.transport("offline")) }
        let keychain = InMemoryKeychainStore()
        let holder = TokenHolder()
        let service = makeService(network: network, keychain: keychain, holder: holder)

        _ = await service.login(email: "javi@futmondo.test", password: "secret")
        await service.logout()

        let inMemory = await service.currentAccessToken()
        XCTAssertNil(inMemory)
        XCTAssertNil(holder.get())
        XCTAssertNil(keychain.peekToken(), "local Keychain entry still cleared")
        let pending = await service.pendingLogoutRevocation
        XCTAssertTrue(pending, "network failure must set pendingLogoutRevocation = true")
    }

    // MARK: - TokenHolder get/set under lock

    func testTokenHolderGetSet() {
        let holder = TokenHolder()
        XCTAssertNil(holder.get())
        holder.set("acc-x")
        XCTAssertEqual(holder.get(), "acc-x")
        holder.set(nil)
        XCTAssertNil(holder.get(), "nil after logout teardown")
    }
}
