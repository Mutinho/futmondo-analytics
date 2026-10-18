import Foundation

#if canImport(Security)
import Security

/// Keychain Services implementation of ``KeychainStore`` (SEC-A1 / REL-A4).
///
/// This type is only compiled where the `Security` framework exists (Apple
/// platforms). On Linux/WSL, `swift test` excludes it so the testable logic
/// (`AuthService`, DTOs, `TokenHolder`, `InMemoryKeychainStore`) still builds.
///
/// Item attributes:
/// - `kSecClass`           = `kSecClassGenericPassword`
/// - `kSecAttrService`     = `"com.futmondo.app.auth"`
/// - `kSecAttrAccount`     = `"refresh_token"`
/// - `kSecAttrAccessible`  = `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`
///   (no iCloud sync, never leaves the device, readable in the background for
///   the startup refresh).
public final class KeychainTokenStore: KeychainStore, @unchecked Sendable {
    /// Logical service namespace for the stored item.
    private let service: String
    /// Account key under which the refresh token is stored.
    private let account: String

    public init(
        service: String = "com.futmondo.app.auth",
        account: String = "refresh_token"
    ) {
        self.service = service
        self.account = account
    }

    /// Base query identifying the single refresh-token item.
    private var baseQuery: [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
    }

    /// Upsert the refresh token: delete any existing item, then add the new one
    /// with a device-only accessibility class. Every `OSStatus` is checked
    /// (REL-A4); a failure is propagated as ``KeychainError``.
    public func saveRefreshToken(_ token: String) throws {
        guard let data = token.data(using: .utf8) else {
            throw KeychainError.encodingFailed
        }

        // Delete first so the add is a clean upsert; a missing item is fine.
        let deleteStatus = SecItemDelete(baseQuery as CFDictionary)
        guard deleteStatus == errSecSuccess || deleteStatus == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(deleteStatus)
        }

        var addQuery = baseQuery
        addQuery[kSecValueData as String] = data
        addQuery[kSecAttrAccessible as String] =
            kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly

        let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
        guard addStatus == errSecSuccess else {
            throw KeychainError.unexpectedStatus(addStatus)
        }
    }

    /// Read the stored refresh token. Returns `nil` on `errSecItemNotFound`
    /// (REL-A4) or when the stored bytes are not valid UTF-8; any other failing
    /// status also resolves to `nil` so startup never hangs on a read error.
    public func readRefreshToken() -> String? {
        var query = baseQuery
        query[kSecReturnData as String] = kCFBooleanTrue
        query[kSecMatchLimit as String] = kSecMatchLimitOne

        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        guard status == errSecSuccess, let data = item as? Data else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }

    /// Delete the stored refresh token. A missing item is not an error
    /// (REL-A4); any other failing status is propagated.
    public func deleteRefreshToken() throws {
        let status = SecItemDelete(baseQuery as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }
}

/// Typed Keychain failures. `OSStatus` is an `Int32`, so this stays `Equatable`
/// and carries no credential material (SEC-A2 / SEC-N4 analogue).
public enum KeychainError: Error, Equatable {
    /// The token string could not be UTF-8 encoded.
    case encodingFailed
    /// A Keychain call returned a non-success, non-"not found" status.
    case unexpectedStatus(OSStatus)
}
#endif
