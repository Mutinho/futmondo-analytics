import Foundation

/// WCAG 2.x contrast helper. Pure math (SwiftUI-free) so it is covered by
/// `swift test` on Linux/WSL. Implements relative luminance and the contrast
/// ratio used to validate color-token pairs against their surface. [BR1.4, NFR1]
public enum ContrastRatio {
    /// WCAG AA threshold for normal-size text.
    public static let normalTextThreshold = 4.5
    /// WCAG AA threshold for large text and non-text UI components.
    public static let largeTextThreshold = 3.0

    /// Relative luminance of a color per WCAG 2.x: linearize each sRGB channel
    /// then weight by the luminance coefficients.
    /// Reference: https://www.w3.org/TR/WCAG20/#relativeluminancedef
    public static func relativeLuminance(_ rgb: DSRGB) -> Double {
        func linearize(_ channel: Int) -> Double {
            let c = Double(channel) / 255.0
            return c <= 0.03928 ? c / 12.92 : pow((c + 0.055) / 1.055, 2.4)
        }
        let r = linearize(rgb.red)
        let g = linearize(rgb.green)
        let b = linearize(rgb.blue)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    }

    /// Contrast ratio between two colors, in `1.0...21.0`. Order-independent
    /// (lighter over darker). Per WCAG: `(L1 + 0.05) / (L2 + 0.05)`.
    public static func ratio(_ a: DSRGB, _ b: DSRGB) -> Double {
        let la = relativeLuminance(a)
        let lb = relativeLuminance(b)
        let lighter = max(la, lb)
        let darker = min(la, lb)
        return (lighter + 0.05) / (darker + 0.05)
    }

    /// Contrast ratio between two token roles resolved for a given appearance.
    /// Returns `nil` if either token's stored hex is malformed.
    public static func ratio(
        _ foreground: DSColorToken,
        on background: DSColorToken,
        appearance: DSAppearance
    ) -> Double? {
        guard
            let fg = foreground.value.rgb(for: appearance),
            let bg = background.value.rgb(for: appearance)
        else {
            return nil
        }
        return ratio(fg, bg)
    }

    /// Whether a foreground/background pair meets the given contrast target for
    /// the appearance. Used to validate the token table (BR1.4); never used to
    /// lower a threshold.
    public static func meets(
        _ foreground: DSColorToken,
        on background: DSColorToken,
        appearance: DSAppearance,
        threshold: Double
    ) -> Bool {
        guard let value = ratio(foreground, on: background, appearance: appearance) else {
            return false
        }
        return value >= threshold
    }
}
