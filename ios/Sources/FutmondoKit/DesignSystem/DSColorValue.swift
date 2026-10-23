import Foundation

/// Appearance mode used to resolve a design-system color value. This is a
/// pure, SwiftUI-free enum so the token logic compiles and is testable on
/// Linux/WSL (`swift test`). SwiftUI accessors in `FutmondoApp` map the
/// system `ColorScheme` onto this type. [BR1.1]
public enum DSAppearance: Sendable, CaseIterable {
    case light
    case dark
}

/// An RGB color with 8-bit channels in the `0...255` range, parsed from a
/// `#RRGGBB` hex string. Pure value type with no SwiftUI/UIKit dependency so
/// the contrast math (see ``ContrastRatio``) can run on Linux/WSL.
public struct DSRGB: Equatable, Sendable {
    /// Red channel, `0...255`.
    public let red: Int
    /// Green channel, `0...255`.
    public let green: Int
    /// Blue channel, `0...255`.
    public let blue: Int

    public init(red: Int, green: Int, blue: Int) {
        self.red = red
        self.green = green
        self.blue = blue
    }

    /// Parses a `#RRGGBB` (or `RRGGBB`) hex string. Returns `nil` for any input
    /// that is not exactly six hex digits (optionally `#`-prefixed). Fail loud
    /// rather than silently coercing malformed values.
    public init?(hex: String) {
        var value = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        if value.hasPrefix("#") {
            value.removeFirst()
        }
        guard value.count == 6, let intValue = Int(value, radix: 16) else {
            return nil
        }
        self.red = (intValue >> 16) & 0xFF
        self.green = (intValue >> 8) & 0xFF
        self.blue = intValue & 0xFF
    }
}

/// A design-system color token carrying its light and dark hex values. The
/// values reproduce the Angular Material 3 theme (source of truth: the
/// `design-system-mapping`). Resolution by appearance is deterministic and
/// SwiftUI-free so it is covered by `swift test`. [FR1, BR1.1]
public struct DSColorValue: Equatable, Sendable {
    /// Hex string (`#RRGGBB`) used in light appearance.
    public let lightHex: String
    /// Hex string (`#RRGGBB`) used in dark appearance.
    public let darkHex: String

    public init(lightHex: String, darkHex: String) {
        self.lightHex = lightHex
        self.darkHex = darkHex
    }

    /// Resolves the hex string for the given appearance. [BR1.1]
    public func hex(for appearance: DSAppearance) -> String {
        switch appearance {
        case .light: return lightHex
        case .dark: return darkHex
        }
    }

    /// Resolves the parsed RGB for the given appearance, or `nil` if the stored
    /// hex is malformed (guards against typos in the token table at test time).
    public func rgb(for appearance: DSAppearance) -> DSRGB? {
        DSRGB(hex: hex(for: appearance))
    }
}

/// The design-system color palette, one ``DSColorValue`` per semantic role.
/// Values mirror the Angular theme exactly (see `design-system-mapping`); the
/// SwiftUI `DSColor` accessor in `FutmondoApp` reads these same roles so the
/// asset catalog and the code stay in lockstep. [FR1]
public enum DSColorToken: String, CaseIterable, Sendable {
    case primary
    case onPrimary
    case tertiary
    case surface
    case onSurface
    case onSurfaceVariant
    case moneyPositive
    case moneyNegative
    case moneyPrize
    case errorContainer
    case cardSurfaceDark

    /// The light/dark values for this role.
    public var value: DSColorValue {
        switch self {
        case .primary:
            return DSColorValue(lightHex: "#2E7D32", darkHex: "#66BB6A")
        case .onPrimary:
            return DSColorValue(lightHex: "#FFFFFF", darkHex: "#0A1F0C")
        case .tertiary:
            return DSColorValue(lightHex: "#7E57C2", darkHex: "#B39DDB")
        case .surface:
            return DSColorValue(lightHex: "#FFFFFF", darkHex: "#121212")
        case .onSurface:
            return DSColorValue(lightHex: "#1C1B1F", darkHex: "#E6E1E5")
        case .onSurfaceVariant:
            return DSColorValue(lightHex: "#49454F", darkHex: "#CAC4D0")
        case .moneyPositive:
            return DSColorValue(lightHex: "#2E7D32", darkHex: "#66BB6A")
        case .moneyNegative:
            return DSColorValue(lightHex: "#D32F2F", darkHex: "#EF5350")
        case .moneyPrize:
            // PREMIOS blue, reproducing the Angular `.card-stat-val.prize`
            // accent. The dark value (`#64B5F6`) is the one rendered on the
            // dark neon-glass card; the light value keeps parity for the
            // (unused in dark-forced app) light appearance. [FR1.3, BR1.4]
            return DSColorValue(lightHex: "#1565C0", darkHex: "#64B5F6")
        case .errorContainer:
            return DSColorValue(lightHex: "#FFEBEE", darkHex: "#3A1416")
        case .cardSurfaceDark:
            // Representative OPAQUE approximation of the dark neon-glass card
            // surface (black ~0.45 over `.ultraThinMaterial` over the dark
            // stadium photo). Used as the deterministic background baseline for
            // the WCAG contrast tests (the live surface is translucent and
            // device-validated). A dark green-tinted charcoal. [BR1.4, NFR1]
            return DSColorValue(lightHex: "#141814", darkHex: "#141814")
        }
    }
}

/// The splash gradient stops (135°), reproduced from the Angular splash. Not a
/// single Color Asset but a three-stop linear gradient. [FR1.3]
public enum DSSplashGradient {
    /// Ordered hex stops of the 135° splash gradient.
    public static let stops: [String] = ["#1B5E20", "#2E7D32", "#43A047"]
}
