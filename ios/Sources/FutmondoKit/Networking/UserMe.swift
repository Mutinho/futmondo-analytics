import Foundation

/// Minimal smoke DTO for `GET /api/v1/user/me`. Used only to validate the
/// access-token pipeline end-to-end in F1; the full user model lands in F2.
public struct UserMe: Decodable, Equatable {
    public let userId: String
    public let email: String

    /// snake_case wire keys from the FastAPI backend.
    private enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case email
    }

    public init(userId: String, email: String) {
        self.userId = userId
        self.email = email
    }
}
