import Foundation

/// The design-system spacing scale, in points. Pure value logic (SwiftUI-free)
/// so `swift test` covers it on Linux/WSL. Values reproduce the Angular theme
/// spacing scale. [FR3]
public enum DSSpacing: String, CaseIterable, Sendable {
    case xs
    case sm
    case md
    case lg
    case xl

    /// The spacing value in points: 4 / 8 / 16 / 24 / 32. [FR3]
    public var points: Double {
        switch self {
        case .xs: return 4
        case .sm: return 8
        case .md: return 16
        case .lg: return 24
        case .xl: return 32
        }
    }
}
