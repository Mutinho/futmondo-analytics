import Foundation

/// Type-erased `Encodable` wrapper so an ``APIRequest`` can carry any encodable
/// body and still be serialized with a single `JSONEncoder` call (NR2).
public struct AnyEncodable: Encodable {
    private let encodeFunc: (Encoder) throws -> Void

    public init<T: Encodable>(_ wrapped: T) {
        self.encodeFunc = wrapped.encode
    }

    public func encode(to encoder: Encoder) throws {
        try encodeFunc(encoder)
    }
}

/// Value describing an HTTP request relative to the client's base URL.
///
/// `path` is joined to the injected base URL (NR4); `headers` are applied
/// verbatim; a non-`nil` `body` is JSON-encoded with `Content-Type:
/// application/json` (NR2).
public struct APIRequest {
    public let method: HTTPMethod
    /// Path relative to the client's base URL (e.g. `/api/v1/user/me`).
    public let path: String
    public var headers: [String: String]
    /// Request body wrapping any `Encodable`; `nil` means no body.
    public var body: AnyEncodable?

    public init(
        method: HTTPMethod,
        path: String,
        headers: [String: String] = [:],
        body: AnyEncodable? = nil
    ) {
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
    }
}

/// Decodable marker for a 2xx response with no body (e.g. `204 No Content`).
///
/// Callers type `T == EmptyResponse` when they expect an empty success payload.
public struct EmptyResponse: Decodable, Equatable {
    public init() {}
}
