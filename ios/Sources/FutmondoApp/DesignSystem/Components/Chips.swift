import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// A small UPPERCASE stat label reproducing the Angular `.card-stat-label`
/// (`font-size: 0.65em; font-weight: 800; text-transform: uppercase;
/// letter-spacing: 0.05em; color: on-surface-variant`). The caller passes the
/// already-uppercased text (e.g. `"SALDO"`) so the literal stays a preserved
/// token. [FR1.2]
@available(iOS 15.0, macOS 12.0, *)
public struct DSStatLabel: View {
    private let text: String

    public init(_ text: String) {
        self.text = text
    }

    public var body: some View {
        Text(text)
            .font(.caption2.weight(.heavy))
            .tracking(0.5)
            .foregroundStyle(DSColor.onSurfaceVariant)
            .accessibilityHidden(true)
    }
}

/// A rounded, tinted badge for a money value, reproducing the Angular
/// `.card-stat-val.badge` (`padding: 2px 8px; border-radius: 4px;` with a
/// positive/negative tint background). Colour is an *additional* carrier — the
/// sign is always present in `value` — so it stays A7-compliant. [FR1.3, A7]
@available(iOS 15.0, macOS 12.0, *)
public struct DSMoneyBadge: View {
    private let value: String
    private let isNegative: Bool

    public init(value: String, isNegative: Bool) {
        self.value = value
        self.isNegative = isNegative
    }

    private var tint: Color { isNegative ? DSColor.moneyNegative : DSColor.moneyPositive }

    public var body: some View {
        Text(value)
            .font(DSFont.h3)
            .foregroundStyle(tint)
            .padding(.horizontal, DSSpacingSwiftUI.sm)
            .padding(.vertical, 2)
            .background(tint.opacity(0.12))
            .clipShape(RoundedRectangle(cornerRadius: 6))
            .accessibilityHidden(true)
    }
}

/// A rounded, bordered chip for navigation-bar / inline controls, reproducing
/// the pill look of the Angular Material outlined controls. Used by the
/// championship selector (D3) and the sort selector (D4): an optional leading
/// SF Symbol, a text label, and an optional trailing chevron. Muted when
/// disabled. The chip renders only its visual shell; the caller wraps it in a
/// `Menu` and owns the accessibility label. [FR2.1, FR3.1]
@available(iOS 15.0, macOS 12.0, *)
public struct DSChip: View {
    private let systemImage: String?
    private let text: String
    private let showsChevron: Bool
    private let isEnabled: Bool

    public init(
        systemImage: String? = nil,
        text: String,
        showsChevron: Bool = true,
        isEnabled: Bool = true
    ) {
        self.systemImage = systemImage
        self.text = text
        self.showsChevron = showsChevron
        self.isEnabled = isEnabled
    }

    private var foreground: Color { isEnabled ? DSColor.primary : DSColor.onSurfaceVariant }

    public var body: some View {
        HStack(spacing: DSSpacingSwiftUI.xs) {
            if let systemImage {
                Image(systemName: systemImage)
                    .font(.caption)
            }
            Text(text)
                .font(DSFont.h3)
                .lineLimit(1)
            if showsChevron {
                Image(systemName: "chevron.down")
                    .font(.caption2.weight(.semibold))
            }
        }
        .foregroundStyle(foreground)
        .padding(.horizontal, DSSpacingSwiftUI.sm)
        .padding(.vertical, DSSpacingSwiftUI.xs)
        .background(DSColor.primary.opacity(isEnabled ? 0.08 : 0.0))
        .overlay(
            Capsule()
                .stroke(foreground.opacity(isEnabled ? 0.4 : 0.25), lineWidth: 1)
        )
        .clipShape(Capsule())
    }
}

#endif // canImport(SwiftUI)
