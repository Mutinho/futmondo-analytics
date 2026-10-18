import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// App entry point (C5). Wires the Apple-SDK-only dependency graph
/// (`KeychainTokenStore` + `TokenHolder` + `URLSessionNetworkClient` +
/// `AuthService`) and starts at ``SplashView`` for auto-login (AR3).
@available(iOS 17.0, macOS 14.0, *)
@main
public struct FutmondoApp: App {
    private let authService: AuthService

    public init() {
        // Build the auth stack. The base URL is the production API over HTTPS;
        // the throwing init rejects any non-https URL (SEC-N1).
        let baseURL = URL(string: "https://futmondo-api.fly.dev")!
        let keychain = KeychainTokenStore()
        let tokenHolder = TokenHolder()
        let service = AuthService(
            network: FutmondoApp.makeNetworkClient(baseURL: baseURL, tokenHolder: tokenHolder),
            keychain: keychain,
            tokenHolder: tokenHolder
        )
        self.authService = service
    }

    public var body: some Scene {
        WindowGroup {
            SplashView(authService: authService)
        }
    }

    /// Build the network client with a provider that reads the holder snapshot
    /// (AR8). Falls back to a provider returning `nil` only if the (https) URL
    /// is somehow rejected, which cannot happen for the constant above.
    private static func makeNetworkClient(baseURL: URL, tokenHolder: TokenHolder) -> NetworkClient {
        do {
            return try URLSessionNetworkClient(
                baseURL: baseURL,
                accessTokenProvider: { tokenHolder.get() }
            )
        } catch {
            // Unreachable for an https constant; fail safe with a client that
            // simply has no token to inject.
            return try! URLSessionNetworkClient(
                baseURL: URL(string: "https://futmondo-api.fly.dev")!,
                accessTokenProvider: { nil }
            )
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
