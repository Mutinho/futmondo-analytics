import Foundation

/// Request body for `POST /auth/login` (AR1).
public struct LoginRequestDTO: Encodable, Equatable, Sendable {
    public let email: String
    public let password: String

    public init(email: String, password: String) {
        self.email = email
        self.password = password
    }
}

/// Response body for `POST /auth/login`. Includes `refresh_token` after the
/// backend adjustment D-01 (Bolt 1). snake_case wire keys from FastAPI.
public struct LoginResponseDTO: Decodable, Equatable, Sendable {
    public let accessToken: String
    public let refreshToken: String
    public let tokenType: String
    public let expiresIn: Int
    public let userId: String
    public let email: String
    public let displayName: String?

    private enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
        case userId = "user_id"
        case email
        case displayName = "display_name"
    }

    public init(
        accessToken: String,
        refreshToken: String,
        tokenType: String,
        expiresIn: Int,
        userId: String,
        email: String,
        displayName: String?
    ) {
        self.accessToken = accessToken
        self.refreshToken = refreshToken
        self.tokenType = tokenType
        self.expiresIn = expiresIn
        self.userId = userId
        self.email = email
        self.displayName = displayName
    }
}

/// Request body for `POST /auth/refresh` (D-01: the refresh token travels in
/// the `X-Refresh-Token` header; this body remains available for parity with
/// the backend contract).
public struct RefreshRequestDTO: Encodable, Equatable, Sendable {
    public let refreshToken: String

    private enum CodingKeys: String, CodingKey {
        case refreshToken = "refresh_token"
    }

    public init(refreshToken: String) {
        self.refreshToken = refreshToken
    }
}

/// Response body for `POST /auth/refresh`. snake_case wire keys.
public struct RefreshResponseDTO: Decodable, Equatable, Sendable {
    public let accessToken: String
    public let expiresIn: Int

    private enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case expiresIn = "expires_in"
    }

    public init(accessToken: String, expiresIn: Int) {
        self.accessToken = accessToken
        self.expiresIn = expiresIn
    }
}
