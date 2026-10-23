import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// An elegant, native confirmation presented as a bottom sheet (medium detent)
/// instead of the plain `confirmationDialog` action sheet. A glass card with an
/// icon badge, title, message, and two DesignSystem buttons (confirm /
/// cancel). Reused by the Calculadora for both "poner a la venta" (W5) and
/// "retirar de la venta" (W6).
@available(iOS 17.0, macOS 14.0, *)
struct ConfirmSheet: View {
    let icon: String
    let title: String
    let message: String
    let confirmLabel: String
    let confirmRole: ButtonRole?
    let onConfirm: () -> Void

    @Environment(\.dismiss) private var dismiss

    private var accent: Color {
        confirmRole == .destructive ? DSColor.moneyNegative : DSColor.primary
    }

    var body: some View {
        VStack(spacing: DSSpacingSwiftUI.lg) {
            ZStack {
                Circle()
                    .fill(accent.opacity(0.15))
                    .frame(width: 64, height: 64)
                Image(systemName: icon)
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(accent)
            }
            .padding(.top, DSSpacingSwiftUI.lg)
            .accessibilityHidden(true)

            VStack(spacing: DSSpacingSwiftUI.xs) {
                Text(title)
                    .font(DSFont.h3)
                    .foregroundStyle(DSColor.onSurface)
                    .multilineTextAlignment(.center)
                Text(message)
                    .font(DSFont.body)
                    .foregroundStyle(DSColor.onSurfaceVariant)
                    .multilineTextAlignment(.center)
            }
            .padding(.horizontal, DSSpacingSwiftUI.lg)

            Spacer(minLength: 0)

            VStack(spacing: DSSpacingSwiftUI.sm) {
                Button {
                    onConfirm()
                    dismiss()
                } label: {
                    Text(confirmLabel)
                        .font(DSFont.body.weight(.bold))
                        .frame(maxWidth: .infinity)
                        .frame(minHeight: 50)
                        .foregroundStyle(DSColor.onPrimary)
                        .background(accent, in: RoundedRectangle(cornerRadius: 14))
                }
                .accessibilityIdentifier("confirm-sheet-confirm")

                Button(role: .cancel) {
                    dismiss()
                } label: {
                    Text("Cancelar")
                        .font(DSFont.body.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .frame(minHeight: 50)
                        .foregroundStyle(DSColor.onSurface)
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 14))
                }
                .accessibilityIdentifier("confirm-sheet-cancel")
            }
            .padding(.horizontal, DSSpacingSwiftUI.lg)
            .padding(.bottom, DSSpacingSwiftUI.lg)
        }
        .frame(maxWidth: .infinity)
        .presentationDetents([.height(340)])
        .presentationDragIndicator(.visible)
        .presentationBackground(.ultraThinMaterial)
        .accessibilityElement(children: .contain)
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
