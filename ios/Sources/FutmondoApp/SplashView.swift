import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Auto-login splash (C5 / AR3 / AR6). On appear it runs
/// `AuthService.bootstrap()` and routes to the authenticated surface, to login,
/// or shows a brief offline banner then falls through to login — it never
/// hangs. The logo shares a `matchedGeometryEffect` with ``LoginView``.
@available(iOS 17.0, macOS 14.0, *)
public struct SplashView: View {
    /// Local splash phase mirroring the interaction-spec states.
    public enum Phase: Equatable {
        case checking
        case resumed
        case expired
        case offline
        case noSession
    }

    private let authService: AuthService
    @State private var viewModel: AuthViewModel
    @State private var phase: Phase = .checking
    @Namespace private var logoNamespace
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(authService: AuthService) {
        self.authService = authService
        _viewModel = State(initialValue: AuthViewModel(authService: authService))
    }

    public var body: some View {
        content
            .animation(reduceMotion ? nil : .default, value: phase)
            .task { await runBootstrap() }
            // Manual login success (from LoginView) must route to the
            // authenticated surface: bootstrap only runs at launch, so without
            // this the view would stay on the login form after a successful
            // login (AR1/AR6). Logout resets the ViewModel to .idle, which must
            // NOT bounce back to the login form here.
            .onChange(of: viewModel.state) { _, newState in
                if newState == .success { phase = .resumed }
            }
    }

    @ViewBuilder
    private var content: some View {
        switch phase {
        case .checking:
            checkingView
        case .resumed:
            // F1 closes here without data screens (F2). A provisional entry
            // point to logout lives alongside the authenticated placeholder.
            authenticatedPlaceholder
        case .offline:
            VStack(spacing: 16) {
                logo
                offlineBanner
                LoginView(viewModel: viewModel, logoNamespace: logoNamespace)
            }
        case .expired, .noSession:
            VStack(spacing: 16) {
                logo
                LoginView(viewModel: viewModel, logoNamespace: logoNamespace)
            }
        }
    }

    private var checkingView: some View {
        VStack(spacing: 16) {
            logo
            ProgressView()
            Text("Recuperando sesión…")
                .font(.callout)
                .foregroundStyle(.secondary)
        }
        .accessibilityElement(children: .combine)
    }

    private var authenticatedPlaceholder: some View {
        VStack(spacing: 16) {
            logo
            Text("Sesión iniciada")
                .font(.headline)
            Button("Cerrar sesión") {
                Task {
                    await viewModel.logout()
                    phase = .noSession
                }
            }
            .buttonStyle(.bordered)
            .frame(minHeight: 44)
            .accessibilityLabel("Cerrar sesión")
        }
    }

    private var offlineBanner: some View {
        Text("Sin conexión. Inicia sesión cuando vuelvas a tener red.")
            .font(.callout)
            .foregroundStyle(.secondary)
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.yellow.opacity(0.15), in: RoundedRectangle(cornerRadius: 10))
    }

    private var logo: some View {
        Image(systemName: "sportscourt.fill")
            .resizable()
            .scaledToFit()
            .frame(width: 72, height: 72)
            .matchedGeometryEffect(id: "logo", in: logoNamespace)
            .accessibilityHidden(true)
    }

    private func runBootstrap() async {
        let state = await authService.bootstrap()
        switch state {
        case .authenticated:
            phase = .resumed
        case .unauthenticated:
            phase = .noSession
        case .offlinePreserved:
            phase = .offline
        }
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
