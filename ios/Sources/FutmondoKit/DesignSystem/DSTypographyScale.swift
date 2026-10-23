import Foundation

/// The design-system typography scale: base point sizes per role. Pure value
/// logic (SwiftUI-free) so `swift test` covers it on Linux/WSL. The SwiftUI
/// `DSFont` accessor in `FutmondoApp` maps these base sizes onto Dynamic Type
/// relative styles (`relativeTo`/`@ScaledMetric`). [FR2]
public enum DSTypographyScale: String, CaseIterable, Sendable {
    case h1
    case h2
    case h3
    case body

    /// The base point size: h1=28 / h2=20 / h3=16 / body=14. [FR2]
    public var baseSize: Double {
        switch self {
        case .h1: return 28
        case .h2: return 20
        case .h3: return 16
        case .body: return 14
        }
    }

    /// The nominal font weight for the role, mirroring the Angular theme
    /// (h1 bold / h2 semibold / h3 semibold / body regular). Expressed as a
    /// SwiftUI-free descriptor so the accessor can map it to `Font.Weight`.
    public var weight: DSFontWeight {
        switch self {
        case .h1: return .bold
        case .h2: return .semibold
        case .h3: return .semibold
        case .body: return .regular
        }
    }

    /// The preferred font family name. The SwiftUI accessor uses Roboto when it
    /// is bundled and falls back to the system font otherwise. [BR1.3]
    public static let preferredFontFamily = "Roboto"
}

/// SwiftUI-free font-weight descriptor so ``DSTypographyScale`` stays testable
/// on Linux/WSL. The SwiftUI `DSFont` accessor maps it to `Font.Weight`.
public enum DSFontWeight: String, Sendable {
    case regular
    case semibold
    case bold
}
