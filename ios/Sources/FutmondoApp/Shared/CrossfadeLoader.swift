import Foundation

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// A real **cross-dissolve** between a loading skeleton and the loaded content.
///
/// Putting `.transition(.opacity)` on the branches of a `switch` does NOT give
/// a reliable crossfade in SwiftUI: the runtime treats the differing subtrees
/// as a replacement (the content "pops" in). This container instead keeps BOTH
/// layers mounted in a `ZStack` and cross-fades their `opacity` from a single
/// `isLoading` flag, so the skeleton fades out exactly as the content fades in.
///
/// The caller passes `isLoading` (true while skeleton should show), the
/// `skeleton` view, and the `content` view. The fade is animated and gated by
/// Reduce Motion. The hidden layer is also `allowsHitTesting(false)` so taps
/// never land on the fading-out skeleton.
@available(iOS 17.0, macOS 14.0, *)
struct CrossfadeLoader<Skeleton: View, Content: View>: View {
    let isLoading: Bool
    @ViewBuilder let skeleton: () -> Skeleton
    @ViewBuilder let content: () -> Content

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            content()
                .opacity(isLoading ? 0 : 1)
                .allowsHitTesting(!isLoading)

            skeleton()
                .opacity(isLoading ? 1 : 0)
                .allowsHitTesting(false)
        }
        .animation(reduceMotion ? nil : .easeInOut(duration: 0.45), value: isLoading)
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
