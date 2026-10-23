import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// Surface container reproducing the Angular `mat-card`: a `surface`-filled
/// rounded rectangle (corner radius 16) wrapping arbitrary content. No
/// interaction of its own. [FR4]
@available(iOS 15.0, macOS 12.0, *)
public struct Card<Content: View>: View {
    private let content: () -> Content

    public init(@ViewBuilder content: @escaping () -> Content) {
        self.content = content
    }

    public var body: some View {
        content()
            .padding(DSSpacingSwiftUI.md)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(DSColor.surface)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(DSColor.onSurfaceVariant.opacity(0.15), lineWidth: 1)
            )
            .accessibilityIdentifier("card")
    }
}

/// Reusable loading indicator reproducing the Angular `mat-spinner`, with an
/// optional message. [FR4]
@available(iOS 15.0, macOS 12.0, *)
public struct LoadingState: View {
    private let message: String?

    public init(message: String? = nil) {
        self.message = message
    }

    public var body: some View {
        VStack(spacing: DSSpacingSwiftUI.sm) {
            ProgressView()
            if let message, !message.isEmpty {
                Text(message)
                    .font(DSFont.body)
                    .foregroundStyle(DSColor.onSurfaceVariant)
            }
        }
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(message ?? "Cargando")
        .accessibilityIdentifier("loading-state")
    }
}

/// Reusable error presentation reproducing the Angular `.error-message`. It
/// combines an icon and text (never color alone) so the error is perceivable
/// regardless of color vision. [FR4, A7]
@available(iOS 15.0, macOS 12.0, *)
public struct ErrorState: View {
    private let message: String

    public init(message: String) {
        self.message = message
    }

    public var body: some View {
        HStack(spacing: DSSpacingSwiftUI.sm) {
            Image(systemName: "exclamationmark.triangle.fill")
                .accessibilityHidden(true)
            Text(message)
                .font(DSFont.body)
        }
        .foregroundStyle(DSColor.moneyNegative)
        .padding(DSSpacingSwiftUI.md)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(DSColor.errorContainer)
        .clipShape(RoundedRectangle(cornerRadius: 10))
        .accessibilityElement(children: .combine)
        .accessibilityLabel(message)
        .accessibilityIdentifier("error-state")
    }
}

#endif // canImport(SwiftUI)
