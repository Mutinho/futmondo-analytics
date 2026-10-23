import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// SwiftUI accessor for the design-system typography scale. Each style maps a
/// `DSTypographyScale` base size onto a Dynamic Type relative style so text
/// scales with the user's text-size setting (BR1.2), and uses Roboto when it is
/// bundled and the system font otherwise (BR1.3). [FR2]
@available(iOS 15.0, macOS 12.0, *)
public enum DSFont {
    public static var h1: Font { font(.h1, relativeTo: .largeTitle) }
    public static var h2: Font { font(.h2, relativeTo: .title2) }
    public static var h3: Font { font(.h3, relativeTo: .headline) }
    public static var body: Font { font(.body, relativeTo: .body) }

    /// Whether Roboto is available in the current process. Evaluated once.
    /// When false, the accessor falls back to the system font. [BR1.3]
    public static let isRobotoAvailable: Bool = {
        #if canImport(UIKit)
        return UIFont(name: DSTypographyScale.preferredFontFamily, size: 12) != nil
        #else
        return false
        #endif
    }()

    /// Builds a Dynamic Type-scaling `Font` for a scale role. Uses a custom
    /// Roboto face relative to `textStyle` when bundled; otherwise a system
    /// font of the same base size relative to the same style. [BR1.2, BR1.3]
    public static func font(
        _ scale: DSTypographyScale,
        relativeTo textStyle: Font.TextStyle
    ) -> Font {
        let weight = scale.weight.swiftUIWeight
        if isRobotoAvailable {
            return .custom(
                DSTypographyScale.preferredFontFamily,
                size: scale.baseSize,
                relativeTo: textStyle
            )
            .weight(weight)
        }
        return .system(textStyle, design: .default).weight(weight)
    }
}

@available(iOS 15.0, macOS 12.0, *)
extension DSFontWeight {
    /// Maps the SwiftUI-free weight descriptor onto `Font.Weight`.
    var swiftUIWeight: Font.Weight {
        switch self {
        case .regular: return .regular
        case .semibold: return .semibold
        case .bold: return .bold
        }
    }
}

#endif // canImport(SwiftUI)
