import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

#if canImport(Observation)
import Observation
#endif

/// UI state for the login/splash surface (AR6). Mirrors the mockup states.
public enum AuthState: Equatable {
    case idle
    case typing
    case loading
    case error(String)
    case success
}

#if canImport(Observation)

/// Observable auth view model (C4 / AR6). Reflects `AuthService` results and
/// NEVER retries (the single retry lives in `AuthService`, ADR-4). Clears the
/// form password after a successful login and on logout (SEC-A3).
@available(iOS 17.0, macOS 14.0, *)
@Observable
public final class AuthViewModel {
    public var state: AuthState = .idle
    public var email: String = "" {
        didSet { markTypingIfNeeded() }
    }
    public var password: String = "" {
        didSet { markTypingIfNeeded() }
    }

    private let authService: AuthService

    public init(authService: AuthService) {
        self.authService = authService
    }

    /// Whether the submit button is enabled (both fields present, not loading).
    public var canSubmit: Bool {
        !email.isEmpty && !password.isEmpty && state != .loading
    }

    private func markTypingIfNeeded() {
        if case .loading = state { return }
        state = (email.isEmpty && password.isEmpty) ? .idle : .typing
    }

    /// Submit the login form (AR1). On success clears the password (SEC-A3).
    @MainActor
    public func submitLogin() async {
        guard canSubmit else { return }
        state = .loading
        let result = await authService.login(email: email, password: password)
        switch result {
        case .success:
            password = ""
            state = .success
        case .failure(let error):
            state = .error(Self.message(for: error))
        }
    }

    /// Log out (AR5) and clear the password (SEC-A3).
    @MainActor
    public func logout() async {
        await authService.logout()
        password = ""
        state = .idle
    }

    /// Map a domain error to a Spanish, user-facing message (no credential
    /// material).
    static func message(for error: AuthError) -> String {
        switch error {
        case .invalidCredentials:
            return "Email o contraseña incorrectos."
        case .network:
            return "No se pudo conectar. Revisa tu conexión e inténtalo de nuevo."
        case .refreshFailed:
            return "Tu sesión ha expirado. Vuelve a iniciar sesión."
        case .unknown:
            return "Ha ocurrido un error inesperado. Inténtalo de nuevo."
        }
    }
}

#endif // canImport(Observation)
#endif // canImport(SwiftUI)
