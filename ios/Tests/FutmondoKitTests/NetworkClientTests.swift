import XCTest
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif
@testable import FutmondoKit

/// URLProtocol stub capturing the outgoing request and returning a scripted
/// response/body or error. Injected through `URLSessionConfiguration.ephemeral`.
final class MockURLProtocol: URLProtocol {
    /// Handler produces either a (response, body) pair or throws to simulate a
    /// transport failure. Also receives the request so tests can inspect it.
    nonisolated(unsafe) static var requestHandler: ((URLRequest) throws -> (HTTPURLResponse, Data))?
    /// Captures the last request that reached the loader (headers included).
    nonisolated(unsafe) static var lastRequest: URLRequest?

    static func reset() {
        requestHandler = nil
        lastRequest = nil
    }

    override class func canInit(with request: URLRequest) -> Bool { true }

    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        MockURLProtocol.lastRequest = request
        guard let handler = MockURLProtocol.requestHandler else {
            client?.urlProtocol(self, didFailWithError: URLError(.unsupportedURL))
            return
        }
        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }

    override func stopLoading() {}
}

final class NetworkClientTests: XCTestCase {
    private let baseURL = URL(string: "https://api.futmondo.test")!

    private func makeSession() -> URLSession {
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [MockURLProtocol.self]
        return URLSession(configuration: config)
    }

    private func makeClient(token: String? = nil) throws -> URLSessionNetworkClient {
        try URLSessionNetworkClient(
            baseURL: baseURL,
            session: makeSession(),
            accessTokenProvider: { token }
        )
    }

    private func httpResponse(_ status: Int) -> HTTPURLResponse {
        HTTPURLResponse(
            url: baseURL,
            statusCode: status,
            httpVersion: "HTTP/1.1",
            headerFields: nil
        )!
    }

    override func setUp() {
        super.setUp()
        MockURLProtocol.reset()
    }

    override func tearDown() {
        MockURLProtocol.reset()
        super.tearDown()
    }

    // MARK: - 1. 2xx decodes into T

    func testSuccess2xxDecodesBody() async throws {
        let json = #"{"user_id":"u-42","email":"javi@futmondo.test"}"#.data(using: .utf8)!
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(200), json) }

        let client = try makeClient(token: "valid-token")
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        switch result {
        case .success(let user):
            XCTAssertEqual(user, UserMe(userId: "u-42", email: "javi@futmondo.test"))
        case .failure(let error):
            XCTFail("Expected success, got \(error)")
        }
    }

    // MARK: - 2. 2xx empty body -> EmptyResponse

    func testSuccess2xxEmptyBodyMapsToEmptyResponse() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(204), Data()) }

        let client = try makeClient(token: "valid-token")
        let result: Result<EmptyResponse, NetworkError> = await client.send(
            APIRequest(method: .delete, path: "/api/v1/session")
        )

        XCTAssertEqual(result, .success(EmptyResponse()))
    }

    // MARK: - 3. 401 -> unauthorized

    func testStatus401MapsToUnauthorized() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(401), Data()) }

        let client = try makeClient()
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        XCTAssertEqual(result, .failure(.unauthorized))
    }

    // MARK: - 4. 403 -> forbidden

    func testStatus403MapsToForbidden() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(403), Data()) }

        let client = try makeClient(token: "valid-token")
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/admin")
        )

        XCTAssertEqual(result, .failure(.forbidden))
    }

    // MARK: - 5. other 4xx -> clientError(status)

    func testStatus404MapsToClientError() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(404), Data()) }

        let client = try makeClient(token: "valid-token")
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/missing")
        )

        XCTAssertEqual(result, .failure(.clientError(404)))
    }

    // MARK: - 6. 5xx -> server(status)

    func testStatus500MapsToServer() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(503), Data()) }

        let client = try makeClient(token: "valid-token")
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        XCTAssertEqual(result, .failure(.server(503)))
    }

    // MARK: - 7. transport failure

    func testTransportFailureMapsToTransport() async throws {
        MockURLProtocol.requestHandler = { _ in
            throw URLError(.notConnectedToInternet)
        }

        let client = try makeClient(token: "valid-token")
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        switch result {
        case .failure(.transport(let message)):
            XCTAssertFalse(message.isEmpty, "transport message should be non-empty")
        default:
            XCTFail("Expected .transport, got \(result)")
        }
    }

    // MARK: - 8. invalid JSON -> decoding

    func testInvalidJSONMapsToDecoding() async throws {
        let badJSON = #"{"user_id":"u-42""#.data(using: .utf8)!  // truncated, invalid
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(200), badJSON) }

        let client = try makeClient(token: "valid-token")
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        switch result {
        case .failure(.decoding(let message)):
            XCTAssertFalse(message.isEmpty, "decoding message should be non-empty")
        default:
            XCTFail("Expected .decoding, got \(result)")
        }
    }

    // MARK: - 9. unexpected status (3xx) -> unexpectedStatus

    func testStatus3xxMapsToUnexpectedStatus() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(302), Data()) }

        let client = try makeClient(token: "valid-token")
        let result: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        XCTAssertEqual(result, .failure(.unexpectedStatus(302)))
    }

    // MARK: - 10. Bearer header present when token provided

    func testBearerHeaderPresentWhenTokenProvided() async throws {
        let json = #"{"user_id":"u-1","email":"a@b.test"}"#.data(using: .utf8)!
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(200), json) }

        let client = try makeClient(token: "secret-token")
        let _: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        let authHeader = MockURLProtocol.lastRequest?.value(forHTTPHeaderField: "Authorization")
        XCTAssertEqual(authHeader, "Bearer secret-token")
    }

    // MARK: - 11. Bearer header absent when no token

    func testBearerHeaderAbsentWhenNoToken() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(401), Data()) }

        let client = try makeClient(token: nil)
        let _: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        let authHeader = MockURLProtocol.lastRequest?.value(forHTTPHeaderField: "Authorization")
        XCTAssertNil(authHeader, "Authorization header must be absent when no token is provided")
    }

    // MARK: - 12. empty token is treated as no token

    func testEmptyTokenDoesNotInjectBearer() async throws {
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(401), Data()) }

        let client = try makeClient(token: "")
        let _: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .get, path: "/api/v1/user/me")
        )

        let authHeader = MockURLProtocol.lastRequest?.value(forHTTPHeaderField: "Authorization")
        XCTAssertNil(authHeader, "Empty token must not inject an Authorization header")
    }

    // MARK: - 13. throwing init rejects non-https base URL

    func testThrowingInitRejectsInsecureBaseURL() {
        XCTAssertThrowsError(
            try URLSessionNetworkClient(
                baseURL: URL(string: "http://api.futmondo.test")!,
                session: makeSession(),
                accessTokenProvider: { nil }
            )
        ) { error in
            XCTAssertEqual(error as? NetworkClientError, .insecureBaseURL)
        }
    }

    // MARK: - 14. throwing init accepts https base URL

    func testThrowingInitAcceptsHTTPSBaseURL() {
        XCTAssertNoThrow(
            try URLSessionNetworkClient(
                baseURL: URL(string: "https://api.futmondo.test")!,
                session: makeSession(),
                accessTokenProvider: { nil }
            )
        )
    }

    // MARK: - 15. URL is built as baseURL + path without encoding the slash

    func testRequestURLJoinsBaseAndPathCorrectly() async throws {
        let json = #"{"user_id":"u-1","email":"a@b.test"}"#.data(using: .utf8)!
        MockURLProtocol.requestHandler = { [self] _ in (httpResponse(200), json) }

        let client = try makeClient(token: "t")
        let _: Result<UserMe, NetworkError> = await client.send(
            APIRequest(method: .post, path: "/auth/login")
        )

        // The absolute URL must be base + path with a single slash, not a
        // percent-encoded or doubled path (regression guard for the old
        // `appendingPathComponent` bug that broke on-device connections).
        XCTAssertEqual(
            MockURLProtocol.lastRequest?.url?.absoluteString,
            "https://api.futmondo.test/auth/login"
        )
    }
}
