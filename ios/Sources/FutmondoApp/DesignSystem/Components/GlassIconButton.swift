import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// A plain SF Symbol label for navigation-bar controls (F2 / iteración 2b).
///
/// On iOS 26 the system toolbar wraps bar-button items in its own floating
/// Liquid-Glass capsule automatically (as in Apple Music). So this control must
/// NOT paint its own material/circle/shadow — doing that stacked a solid
/// whitish bubble on top of the native glass. It therefore renders just the
/// symbol (tinted, and dimmed when disabled) and lets the toolbar supply the
/// glass. Reused by the trophy selector, the sort button and the settings menu
/// so the leading/trailing controls stay symmetric.
///
/// Foreground (F2 / iteración 2d): the enabled symbol is WHITE
/// (`DSColor.onSurface`) so the three glass controls match the white large
/// title over the dark stadium background; the disabled/muted state stays a
/// dimmed `onSurfaceVariant`. The native toolbar still supplies the glass
/// capsule — this control paints no material/circle/shadow of its own.
@available(iOS 15.0, macOS 12.0, *)
public struct DSGlassIcon: View {
    private let systemImage: String
    private let isEnabled: Bool

    public init(systemImage: String, isEnabled: Bool = true) {
        self.systemImage = systemImage
        self.isEnabled = isEnabled
    }

    private var foreground: Color { isEnabled ? DSColor.onSurface : DSColor.onSurfaceVariant }

    public var body: some View {
        Image(systemName: systemImage)
            .font(.system(size: 17, weight: .semibold))
            .foregroundStyle(foreground.opacity(isEnabled ? 1.0 : 0.5))
    }
}

#endif // canImport(SwiftUI)
