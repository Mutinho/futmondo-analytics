import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// Design-system elevation tokens, reproducing the soft shadows of the Angular
/// `mat-card` / `.team-card` (`box-shadow: 0 2px 8px rgba(0,0,0,0.08)`). Kept as
/// a small, reusable token set so cards, chips, and future surfaces share one
/// shadow vocabulary instead of ad-hoc per-view shadows. SwiftUI-only (guarded),
/// Apple-SDK only (cost 0 €). [FR4]
@available(iOS 15.0, macOS 12.0, *)
public enum DSElevation {
    /// A single elevation level: shadow colour opacity, blur radius, and the
    /// vertical offset of the drop shadow.
    public struct Level: Sendable {
        public let opacity: Double
        public let radius: CGFloat
        public let y: CGFloat

        public init(opacity: Double, radius: CGFloat, y: CGFloat) {
            self.opacity = opacity
            self.radius = radius
            self.y = y
        }
    }

    /// Resting card elevation — matches the Angular `.team-card` resting shadow
    /// (`0 2px 8px rgba(0,0,0,0.08)`).
    public static let card = Level(opacity: 0.08, radius: 8, y: 2)

    /// Lower elevation for chips/menus so they read as raised but subtle.
    public static let chip = Level(opacity: 0.06, radius: 4, y: 1)

    /// Soft neon-green glow for the dark glass cards (iteración 2c): a low
    /// opacity, generous blur, no vertical offset so the halo surrounds the
    /// card evenly over the dark stadium photo. The glow COLOUR is applied by
    /// the caller (`NeonGlassCard`) using the DS green; the level carries only
    /// the geometry + opacity.
    public static let neonGlow = Level(opacity: 0.35, radius: 14, y: 0)
}

@available(iOS 15.0, macOS 12.0, *)
extension View {
    /// Applies a design-system elevation level as a drop shadow. The shadow
    /// colour is black at the level's opacity, matching the Angular theme's
    /// `rgba(0,0,0,·)` shadows (which it uses in both light and dark). [FR4]
    public func dsShadow(_ level: DSElevation.Level = DSElevation.card) -> some View {
        self.shadow(
            color: Color.black.opacity(level.opacity),
            radius: level.radius,
            x: 0,
            y: level.y
        )
    }
}

/// An elevated surface card: the `surface`-filled rounded rectangle of ``Card``
/// plus a soft drop shadow (``DSElevation/card``) and generous padding, so a
/// list of these reads as separate raised cards like the Angular cards view.
/// Reuses the same corner radius (16) and surface token as ``Card`` to stay in
/// lockstep with the catalog. [FR4]
@available(iOS 15.0, macOS 12.0, *)
public struct ElevatedCard<Content: View>: View {
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
                    .stroke(DSColor.onSurfaceVariant.opacity(0.12), lineWidth: 1)
            )
            .dsShadow(DSElevation.card)
            .accessibilityIdentifier("elevated-card")
    }
}

/// A DARK NEON-GLASS card (iteración 2c): the dark-translucent surface the
/// owner validated on device for the budget rows over the almost-black stadium
/// photo. A rounded rectangle whose background is black at ~0.45 opacity over
/// `.ultraThinMaterial` (so it reads as dark glass over the photo), a subtle
/// neon-green border (DS green at low alpha), a soft green glow
/// (``DSElevation/neonGlow`` tinted green), and the same corner radius (16) and
/// padding vocabulary as ``Card`` / ``ElevatedCard`` so the catalog is
/// untouched and `BudgetRow` can simply repoint to this style. [FR1.2, FR4]
///
/// Why a solid black-over-material stack rather than a single translucent
/// colour: `.ultraThinMaterial` already samples the photo for the glass blur;
/// the black-0.45 layer on top darkens it enough that WHITE / green / blue text
/// stays ≥4.5:1 (validated by the ``ContrastRatio`` tests against the opaque
/// ``DSColorToken/cardSurfaceDark`` baseline). [BR1.4, NFR1]
@available(iOS 15.0, macOS 12.0, *)
public struct NeonGlassCard<Content: View>: View {
    private let content: () -> Content

    /// Corner radius shared with ``Card`` / ``ElevatedCard``.
    private let cornerRadius: CGFloat = 16
    /// Neon-green border alpha (subtle halo, 0.3–0.4 per the design direction).
    private let borderAlpha: Double = 0.35

    public init(@ViewBuilder content: @escaping () -> Content) {
        self.content = content
    }

    public var body: some View {
        content()
            .padding(DSSpacingSwiftUI.md)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(glassSurface)
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius)
                    .stroke(DSColor.primary.opacity(borderAlpha), lineWidth: 1)
            )
            .shadow(
                color: DSColor.primary.opacity(DSElevation.neonGlow.opacity),
                radius: DSElevation.neonGlow.radius,
                x: 0,
                y: DSElevation.neonGlow.y
            )
            .accessibilityIdentifier("neon-glass-card")
    }

    /// The dark-glass fill: black at ~0.45 over `.ultraThinMaterial`, clipped to
    /// the shared corner radius.
    private var glassSurface: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .fill(Color.black.opacity(0.45))
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: cornerRadius))
    }
}

#endif // canImport(SwiftUI)
