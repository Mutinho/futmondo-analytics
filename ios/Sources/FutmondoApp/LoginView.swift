import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Native login screen (C5 / AR6). Mirrors refined-mockups: email + password
/// fields with autofill, a visibility toggle, a disabled-until-valid submit
/// button, an actionable error banner, haptics, and a shake animation that is
/// suppressed under Reduce Motion.
@available(iOS 17.0, macOS 14.0, *)
public struct LoginView: View {
    @Bindable private var viewModel: AuthViewModel
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    /// Namespace for the logo's `matchedGeometryEffect` shared with the splash.
    private var logoNamespace: Namespace.ID

    @State private var isPasswordVisible = false
    @State private var shakeTrigger = 0
    @FocusState private var focusedField: Field?

    private enum Field: Hashable {
        case email
        case password
    }

    public init(viewModel: AuthViewModel, logoNamespace: Namespace.ID) {
        self.viewModel = viewModel
        self.logoNamespace = logoNamespace
    }

    public var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "sportscourt.fill")
                .resizable()
                .scaledToFit()
                .frame(width: 72, height: 72)
                .matchedGeometryEffect(id: "logo", in: logoNamespace)
                .accessibilityHidden(true)

            Text("Futmondo Analytics")
                .font(.title2.bold())

            card
        }
        .padding(24)
        .animation(reduceMotion ? nil : .default, value: viewModel.state)
    }

    private var card: some View {
        VStack(spacing: 16) {
            if case .error(let message) = viewModel.state {
                errorBanner(message)
            }

            TextField("Email", text: $viewModel.email)
                .textContentType(.username)
                #if os(iOS)
                .keyboardType(.emailAddress)
                .textInputAutocapitalization(.never)
                #endif
                .disableAutocorrection(true)
                .focused($focusedField, equals: .email)
                .submitLabel(.next)
                .onSubmit { focusedField = .password }
                .accessibilityLabel("Email")

            passwordField

            submitButton
        }
        .padding(20)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
        .modifier(ShakeEffect(animatableData: CGFloat(shakeTrigger)))
        .onChange(of: viewModel.state) { _, newState in
            if case .error = newState, !reduceMotion {
                withAnimation(.default) { shakeTrigger += 1 }
            }
        }
        #if os(iOS)
        .sensoryFeedback(.success, trigger: viewModel.state == .success)
        .sensoryFeedback(.error, trigger: isErrorState)
        #endif
    }

    @ViewBuilder
    private var passwordField: some View {
        HStack {
            Group {
                if isPasswordVisible {
                    TextField("Contraseña", text: $viewModel.password)
                } else {
                    SecureField("Contraseña", text: $viewModel.password)
                }
            }
            .textContentType(.password)
            .focused($focusedField, equals: .password)
            .submitLabel(.go)
            .onSubmit { Task { await viewModel.submitLogin() } }
            .accessibilityLabel("Contraseña")

            Button {
                isPasswordVisible.toggle()
            } label: {
                Image(systemName: isPasswordVisible ? "eye.slash.fill" : "eye.fill")
                    #if os(iOS)
                    .symbolEffect(.bounce, value: isPasswordVisible)
                    #endif
            }
            .accessibilityLabel(isPasswordVisible ? "Ocultar contraseña" : "Mostrar contraseña")
            .frame(minWidth: 44, minHeight: 44)
        }
    }

    private var submitButton: some View {
        Button {
            Task { await viewModel.submitLogin() }
        } label: {
            HStack {
                if viewModel.state == .loading {
                    ProgressView()
                }
                Text("Iniciar sesión")
                    .frame(maxWidth: .infinity)
            }
            .frame(minHeight: 44)
        }
        .buttonStyle(.borderedProminent)
        .disabled(!viewModel.canSubmit)
        .accessibilityLabel("Iniciar sesión")
    }

    private func errorBanner(_ message: String) -> some View {
        HStack(spacing: 8) {
            Image(systemName: "exclamationmark.triangle.fill")
            Text(message)
                .font(.callout)
        }
        .foregroundStyle(.red)
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.red.opacity(0.12), in: RoundedRectangle(cornerRadius: 10))
        // Error is conveyed by text + icon, not color alone (A-x accessibility).
        .accessibilityElement(children: .combine)
    }

    private var isErrorState: Bool {
        if case .error = viewModel.state { return true }
        return false
    }
}

/// Horizontal shake used on a login error (suppressed under Reduce Motion by
/// not animating `shakeTrigger`).
private struct ShakeEffect: GeometryEffect {
    var amount: CGFloat = 8
    var shakesPerUnit = 3
    var animatableData: CGFloat

    func effectValue(size: CGSize) -> ProjectionTransform {
        let translation = amount * sin(animatableData * .pi * CGFloat(shakesPerUnit))
        return ProjectionTransform(CGAffineTransform(translationX: translation, y: 0))
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
