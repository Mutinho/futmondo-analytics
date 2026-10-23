import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Native login screen (C5 / AR6). Mirrors refined-mockups: email + password
/// fields with autofill, a visibility toggle, a disabled-until-valid submit
/// button, an actionable error banner, haptics, and a shake animation that is
/// suppressed under Reduce Motion.
///
/// U2 (`u2-login-theming`): the visual layer is re-skinned with the U1
/// `DesignSystem` library — `Card`, `TextInputField`, `PrimaryButton`,
/// `ErrorState` and the `DSColor` / `DSFont` / `DSSpacing` tokens — WITHOUT
/// changing behavior, layout or the public API. The business logic stays in
/// `AuthViewModel` (F1), which U2 does not touch. See `code-summary.md` for the
/// U1↔U2 contract notes (email-field modifier propagation; password visibility
/// toggle kept from F1).
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
        VStack(spacing: DSSpacingSwiftUI.lg) {
            Image(systemName: "sportscourt.fill")
                .resizable()
                .scaledToFit()
                .frame(width: 72, height: 72)
                .matchedGeometryEffect(id: "logo", in: logoNamespace)
                .foregroundStyle(DSColor.primary)
                .accessibilityHidden(true)

            Text("Futmondo Analytics")
                .font(DSFont.h1)
                .foregroundStyle(DSColor.onSurface)

            card
        }
        .padding(DSSpacingSwiftUI.lg)
        .animation(reduceMotion ? nil : .default, value: viewModel.state)
    }

    private var card: some View {
        Card {
            VStack(spacing: DSSpacingSwiftUI.md) {
                if case .error(let message) = viewModel.state {
                    // U1 ErrorState conveys the error by icon + text + token
                    // color (A7), replacing F1's ad-hoc red banner.
                    ErrorState(message: message)
                }

                emailField

                passwordField

                // U1 PrimaryButton: loading takes precedence over disabled
                // (BR2.1). Behavior matches F1's `.borderedProminent`.
                PrimaryButton(
                    title: "Iniciar sesión",
                    isLoading: viewModel.state == .loading,
                    isEnabled: viewModel.canSubmit,
                    action: { Task { await viewModel.submitLogin() } }
                )
                .accessibilityLabel("Iniciar sesión")
            }
        }
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

    /// Email field re-skinned with U1 `TextInputField`. The F1 keyboard,
    /// autofill, focus and submit behavior is preserved via modifiers applied
    /// to the component: `.keyboardType`, `.textContentType`,
    /// `.textInputAutocapitalization`, `.disableAutocorrection`, `.focused`,
    /// `.submitLabel` and `.onSubmit` propagate through SwiftUI to the inner
    /// `TextField` (see code-summary contract note).
    private var emailField: some View {
        TextInputField(
            label: "Email",
            text: $viewModel.email,
            icon: Image(systemName: "envelope")
        )
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
    }

    /// Password field. U1's `TextInputField(isSecure:)` encapsulates its own
    /// `@FocusState` and visibility toggle, which F1 must own (external
    /// email→password focus chain, local `isPasswordVisible`, `.onSubmit`
    /// triggering submit). To preserve F1 behavior exactly without changing
    /// U1's public API, the field keeps F1's secure/plain switch and eye button,
    /// re-skinned with U1 tokens and border treatment (contract note in
    /// code-summary). [FR6.1, NFR2.4]
    @ViewBuilder
    private var passwordField: some View {
        HStack(spacing: DSSpacingSwiftUI.sm) {
            Image(systemName: "lock")
                .foregroundStyle(DSColor.onSurfaceVariant)
                .accessibilityHidden(true)

            Group {
                if isPasswordVisible {
                    TextField("Contraseña", text: $viewModel.password)
                } else {
                    SecureField("Contraseña", text: $viewModel.password)
                }
            }
            .font(DSFont.body)
            .foregroundStyle(DSColor.onSurface)
            .textContentType(.password)
            .focused($focusedField, equals: .password)
            .submitLabel(.go)
            .onSubmit { Task { await viewModel.submitLogin() } }
            .accessibilityLabel("Contraseña")

            Button {
                isPasswordVisible.toggle()
            } label: {
                Image(systemName: isPasswordVisible ? "eye.slash.fill" : "eye.fill")
                    .foregroundStyle(DSColor.onSurfaceVariant)
                    #if os(iOS)
                    .symbolEffect(.bounce, value: isPasswordVisible)
                    #endif
            }
            .accessibilityLabel(isPasswordVisible ? "Ocultar contraseña" : "Mostrar contraseña")
            .frame(minWidth: 44, minHeight: 44)
        }
        .padding(DSSpacingSwiftUI.sm)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(
                    focusedField == .password ? DSColor.primary : DSColor.onSurfaceVariant,
                    lineWidth: 1
                )
        )
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
