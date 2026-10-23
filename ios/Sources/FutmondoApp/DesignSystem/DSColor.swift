import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// SwiftUI accessor for the design-system color tokens. Resolves each role to a
/// `Color` that adapts to light/dark automatically.
///
/// Color source: the values are defined in code here (not an `.xcassets`
/// catalog) so the package compiles on Linux/WSL where asset-catalog
/// compilation is unavailable; the hex values are the single source of truth in
/// `FutmondoKit.DSColorToken` (reproducing the Angular Material 3 theme). On
/// Apple platforms the dynamic provider picks the dark value under
/// `.dark` user interface style. [FR1, BR1.1]
@available(iOS 15.0, macOS 12.0, *)
public enum DSColor {
    public static var primary: Color { color(.primary) }
    public static var onPrimary: Color { color(.onPrimary) }
    public static var tertiary: Color { color(.tertiary) }
    public static var surface: Color { color(.surface) }
    public static var onSurface: Color { color(.onSurface) }
    public static var onSurfaceVariant: Color { color(.onSurfaceVariant) }
    public static var moneyPositive: Color { color(.moneyPositive) }
    public static var moneyNegative: Color { color(.moneyNegative) }
    public static var moneyPrize: Color { color(.moneyPrize) }
    public static var errorContainer: Color { color(.errorContainer) }
    public static var cardSurfaceDark: Color { color(.cardSurfaceDark) }

    /// The 135° splash gradient reproduced from the Angular splash. [FR1.3]
    public static var splashGradient: LinearGradient {
        LinearGradient(
            colors: DSSplashGradient.stops.map { Color(hex: $0) },
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    /// Resolves a token role to an appearance-adaptive `Color`.
    public static func color(_ token: DSColorToken) -> Color {
        #if canImport(UIKit)
        return Color(uiColor: UIColor { traits in
            let appearance: DSAppearance = traits.userInterfaceStyle == .dark ? .dark : .light
            return UIColor(hex: token.value.hex(for: appearance))
        })
        #else
        // On non-UIKit platforms (macOS/Linux dev builds) fall back to the
        // light value; device rendering uses the dynamic UIColor above.
        return Color(hex: token.value.hex(for: .light))
        #endif
    }
}

@available(iOS 15.0, macOS 12.0, *)
extension Color {
    /// Builds a `Color` from a `#RRGGBB` hex string, falling back to clear for a
    /// malformed value (the token table is validated by `swift test`).
    init(hex: String) {
        guard let rgb = DSRGB(hex: hex) else {
            self = .clear
            return
        }
        self = Color(
            red: Double(rgb.red) / 255.0,
            green: Double(rgb.green) / 255.0,
            blue: Double(rgb.blue) / 255.0
        )
    }
}

#if canImport(UIKit)
import UIKit

extension UIColor {
    /// Builds a `UIColor` from a `#RRGGBB` hex string, falling back to clear.
    convenience init(hex: String) {
        guard let rgb = DSRGB(hex: hex) else {
            self.init(white: 0, alpha: 0)
            return
        }
        self.init(
            red: CGFloat(rgb.red) / 255.0,
            green: CGFloat(rgb.green) / 255.0,
            blue: CGFloat(rgb.blue) / 255.0,
            alpha: 1.0
        )
    }
}
#endif

#endif // canImport(SwiftUI)
