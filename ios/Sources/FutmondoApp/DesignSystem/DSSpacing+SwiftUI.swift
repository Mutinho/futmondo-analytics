import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// SwiftUI accessor for the design-system spacing scale. Exposes each step as a
/// `CGFloat`, reading the single source of truth in `FutmondoKit.DSSpacing`.
/// [FR3]
@available(iOS 15.0, macOS 12.0, *)
public enum DSSpacingSwiftUI {
    public static var xs: CGFloat { CGFloat(DSSpacing.xs.points) }
    public static var sm: CGFloat { CGFloat(DSSpacing.sm.points) }
    public static var md: CGFloat { CGFloat(DSSpacing.md.points) }
    public static var lg: CGFloat { CGFloat(DSSpacing.lg.points) }
    public static var xl: CGFloat { CGFloat(DSSpacing.xl.points) }

    /// Resolves any spacing step to a `CGFloat`.
    public static func value(_ step: DSSpacing) -> CGFloat { CGFloat(step.points) }
}

#endif // canImport(SwiftUI)
