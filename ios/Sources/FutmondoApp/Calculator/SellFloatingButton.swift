import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Floating "Vender (N)" CTA (FR8.1 / BR8.1). Shown as a bottom overlay only
/// when at least one player is selected. Tapping it asks `CalculatorView` to
/// present the sell confirmation; it is disabled while a write is in flight.
@available(iOS 17.0, macOS 14.0, *)
struct SellFloatingButton: View {
    let count: Int
    let isWriting: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: DSSpacingSwiftUI.xs) {
                if isWriting {
                    ProgressView()
                        .tint(DSColor.primary)
                } else {
                    Image(systemName: "tag.fill")
                        .font(.footnote.weight(.bold))
                        .accessibilityHidden(true)
                }
                Text("Vender (\(count))")
                    .font(.subheadline.weight(.bold))
                    .lineLimit(1)
            }
            .foregroundStyle(DSColor.primary)
            .padding(.horizontal, DSSpacingSwiftUI.md)
            .padding(.vertical, DSSpacingSwiftUI.sm)
            .background(.ultraThinMaterial, in: Capsule())
            .background(Color.black.opacity(0.35), in: Capsule())
            .overlay(Capsule().stroke(DSColor.primary.opacity(0.55), lineWidth: 1))
            .shadow(color: .black.opacity(0.3), radius: 8, y: 3)
        }
        .disabled(isWriting)
        .opacity(isWriting ? 0.7 : 1)
        .accessibilityLabel("Poner a la venta \(count) jugador(es) seleccionado(s)")
        .accessibilityIdentifier("calculator-sell-button")
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
