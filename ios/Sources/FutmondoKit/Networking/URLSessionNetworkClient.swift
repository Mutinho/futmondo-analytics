import Foundation
#if canImport(FoundationNetworking)
// On Linux/WSL the URLSession networking API lives in a separate module.
import FoundationNetworking
#endif

/// `URLSession`-backed ``NetworkClient``. Apple SDK only (NR6).
///
/// Security invariants:
/// - `init` is throwing and rejects any non-`https` base URL (SEC-N1); this is
///   a propagated typed error, not a `-Ounchecked`-eliminable assertion.
/// - The access token is read from `accessTokenProvider` on every request and
///   placed only on the local `URLRequest`; it is never stored on the client
///   nor logged (SEC-N2 / SEC-N3).
public final class URLSessionNetworkClient: NetworkClient, @unchecked Sendable {
    private let baseURL: URL
    private let session: URLSession
    private let accessTokenProvider: @Sendable () -> String?
    private let encoder: JSONEncoder
    private let decoder: JSONDecoder

    public init(
        baseURL: URL,
        session: URLSession = .shared,
        accessTokenProvider: @escaping @Sendable () -> String?
    ) throws {
        guard baseURL.scheme?.lowercased() == "https" else {
            throw NetworkClientError.insecureBaseURL
        }
        self.baseURL = baseURL
        self.session = session
        self.accessTokenProvider = accessTokenProvider
        self.encoder = JSONEncoder()
        self.decoder = JSONDecoder()
    }

    public func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError> {
        // Build the URLRequest (NR1, NR2, NR4).
        let urlRequest: URLRequest
        do {
            urlRequest = try buildURLRequest(from: request)
        } catch let error as NetworkError {
            return .failure(error)
        } catch {
            return .failure(.transport(error.localizedDescription))
        }

        // Execute and map the outcome (NR3).
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: urlRequest)
        } catch is CancellationError {
            return .failure(.cancelled)
        } catch let urlError as URLError where urlError.code == .cancelled {
            // URLSession surfaces task cancellation as URLError(.cancelled).
            return .failure(.cancelled)
        } catch {
            // Only the localized description crosses the boundary (SEC-N4).
            return .failure(.transport(error.localizedDescription))
        }

        guard let http = response as? HTTPURLResponse else {
            return .failure(.transport("Non-HTTP response"))
        }

        return map(status: http.statusCode, data: data)
    }

    // MARK: - Request building

    private func buildURLRequest(from request: APIRequest) throws -> URLRequest {
        // Build the URL by string concatenation of baseURL + path, normalizing
        // the slash. `URL.appendingPathComponent` treats the whole argument as a
        // SINGLE path segment and percent-encodes it, so a path like
        // "/auth/login" would become a malformed URL (encoded slashes / double
        // slashes) and the request would fail to connect. Here we join on a
        // single "/" and parse the absolute string.
        let base = baseURL.absoluteString.hasSuffix("/")
            ? String(baseURL.absoluteString.dropLast())
            : baseURL.absoluteString
        let path = request.path.hasPrefix("/") ? request.path : "/\(request.path)"
        guard let url = URL(string: base + path) else {
            throw NetworkError.transport("Invalid URL: \(base + path)")
        }
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = request.method.rawValue

        for (field, value) in request.headers {
            urlRequest.setValue(value, forHTTPHeaderField: field)
        }

        // NR1: inject Bearer only when a non-empty token is provided; the token
        // is not retained anywhere on the client.
        if let token = accessTokenProvider(), !token.isEmpty {
            urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        // NR2: encode the body as JSON when present.
        if let body = request.body {
            do {
                urlRequest.httpBody = try encoder.encode(body)
            } catch {
                throw NetworkError.decoding(error.localizedDescription)
            }
            if urlRequest.value(forHTTPHeaderField: "Content-Type") == nil {
                urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
            }
        }

        return urlRequest
    }

    // MARK: - Status mapping (NR3)

    private func map<T: Decodable>(status: Int, data: Data) -> Result<T, NetworkError> {
        switch status {
        case 200...299:
            return decodeSuccess(data: data)
        case 401:
            return .failure(.unauthorized)
        case 403:
            return .failure(.forbidden)
        case 400...499:
            return .failure(.clientError(status))
        case 500...599:
            return .failure(.server(status))
        default:
            // 1xx / 3xx or anything else not contemplated.
            return .failure(.unexpectedStatus(status))
        }
    }

    private func decodeSuccess<T: Decodable>(data: Data) -> Result<T, NetworkError> {
        // 2xx with no body: succeed only when the caller typed EmptyResponse.
        if data.isEmpty {
            if let empty = EmptyResponse() as? T {
                return .success(empty)
            }
            return .failure(.decoding("Empty 2xx body for non-EmptyResponse type \(T.self)"))
        }

        // A caller may type EmptyResponse even when the server returned a body:
        // treat it as success without decoding the payload.
        if let empty = EmptyResponse() as? T {
            return .success(empty)
        }

        do {
            let value = try decoder.decode(T.self, from: data)
            return .success(value)
        } catch {
            return .failure(.decoding(error.localizedDescription))
        }
    }
}
