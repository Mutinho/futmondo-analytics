import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// Primary call-to-action button reproducing the Angular
/// `mat-flat-button color="primary"`. Implements the three states normal /
/// disabled / loading, where loading takes precedence over disabled: a loading
/// button shows a spinner and blocks the tap regardless of `isEnabled`.
/// [FR4.1, BR2.1]
@available(iOS 15.0, macOS 12.0, *)
public struct PrimaryButton: View {
    private let title: String
    private let action: () -> Void
    private let isLoading: Bool
    private let isEnabled: Bool

    public init(
        title: String,
        isLoading: Bool = false,
        isEnabled: Bool = true,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.action = action
        self.isLoading = isLoading
        self.isEnabled = isEnabled
    }

    /// Loading precedence over disabled (BR2.1): a loading button is never
    /// tappable; otherwise it follows `isEnabled`.
    private var isInteractionBlocked: Bool { isLoading || !isEnabled }

    public var body: some View {
        Button(action: action) {
            ZStack {
                // Keep the label in the layout while loading so the button does
                // not resize; the spinner overlays it.
                Text(title)
                    .font(DSFont.h3)
                    .opacity(isLoading ? 0 : 1)

                if isLoading {
                    ProgressView()
                }
            }
            .frame(maxWidth: .infinity, minHeight: 44) // ≥44 pt touch target (NFR3)
            .padding(.horizontal, DSSpacingSwiftUI.md)
            .foregroundStyle(DSColor.onPrimary)
            .background(DSColor.primary.opacity(isEnabled || isLoading ? 1 : 0.5))
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
        .disabled(isInteractionBlocked)
        .accessibilityLabel(title)
        .accessibilityAddTraits(.isButton)
        .accessibilityIdentifier("primary-button")
        // Convey loading to VoiceOver by text, not color alone (A7).
        .accessibilityValue(isLoading ? Text("Cargando") : Text(""))
    }
}

#endif // canImport(SwiftUI)
