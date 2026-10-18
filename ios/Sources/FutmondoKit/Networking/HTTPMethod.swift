import Foundation

/// Supported HTTP verbs for an ``APIRequest``.
///
/// The raw value is the exact method token placed on the `URLRequest`.
public enum HTTPMethod: String, Equatable, Sendable {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}
