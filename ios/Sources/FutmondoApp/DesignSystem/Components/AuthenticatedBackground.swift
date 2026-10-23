import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// Full-bleed sporty background for the AUTHENTICATED surface only (F2 /
/// iteración 2b). It loads the packaged `background.jpg` resource via
/// `Bundle.module`, scales it to fill while clipped and ignoring safe areas,
/// and lays a legibility scrim over it so card text and stat labels keep
/// adequate contrast over the dark photo (NFR1/NFR5). The elevated cards and
/// the floating Liquid-Glass tab bar sit above it.
///
/// If the resource cannot be resolved (e.g. a Linux/WSL build where the asset
/// is not materialised), it degrades gracefully to a plain `DSColor.surface`
/// background — never a crash, never a blank asset. The SwiftUI runtime image
/// path (`Image("background", bundle:)`) is used when it resolves; otherwise
/// the UIKit `UIImage(named:in:with:)` fallback is tried before the solid
/// colour. This modifier is applied to EVERY authenticated screen (Budget, Market, detail) so the background is transversal; it
/// never touches `SplashView`'s login/splash visuals.
@available(iOS 15.0, macOS 12.0, *)
public struct AuthenticatedBackground: ViewModifier {
    public init() {}

    public func body(content: Content) -> some View {
        content
            .background(backdrop)
    }

    @ViewBuilder
    private var backdrop: some View {
        ZStack {
            // Solid fallback is always present underneath, so a missing asset
            // degrades to a clean surface rather than a blank/black screen.
            DSColor.surface
                .ignoresSafeArea()

            if let image = Self.backgroundImage {
                image
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
                    .clipped()
                    .accessibilityHidden(true)

                // Legibility scrim: a subtle dark gradient (denser at the
                // bottom where the stats/tab bar live) keeps text contrast over
                // the photo (NFR1/NFR5). Combined with the glass/elevated
                // surfaces above it.
                LinearGradient(
                    colors: [
                        Color.black.opacity(0.25),
                        Color.black.opacity(0.45)
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                .accessibilityHidden(true)
            }
        }
    }

    /// The packaged background as a SwiftUI `Image`, or `nil` when it cannot be
    /// resolved (so the caller degrades to the solid fallback). Resolved once.
    static let backgroundImage: Image? = {
        #if canImport(UIKit)
        // Load the packaged jpg by its bundle URL — the most reliable path for a
        // `.process`-ed resource file (UIImage(named:) does not reliably resolve
        // a loose jpg outside an .xcassets). Fall back to named:, then to nil
        // (solid DSColor.surface) so a missing asset never crashes.
        if let url = Bundle.module.url(forResource: "background", withExtension: "jpg"),
           let uiImage = UIImage(contentsOfFile: url.path) {
            return Image(uiImage: uiImage)
        }
        if let uiImage = UIImage(named: "background", in: .module, with: nil) {
            return Image(uiImage: uiImage)
        }
        return nil
        #else
        // On non-UIKit dev builds there is no asset pipeline; use the solid
        // fallback. Device (iOS) always takes the UIKit path above.
        return nil
        #endif
    }()
}

@available(iOS 15.0, macOS 12.0, *)
extension View {
    /// Applies the authenticated-surface sporty background + legibility scrim.
    /// Apply to EVERY authenticated screen (Presupuesto, Mercado, detalle) so the sporty background is transversal; never to SplashView/Login.
    public func authenticatedBackground() -> some View {
        modifier(AuthenticatedBackground())
    }
}

#endif // canImport(SwiftUI)
