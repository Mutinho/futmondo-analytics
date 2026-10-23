import Foundation

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// A reusable **animated aurora fill** for skeleton placeholders: instead of a
/// flat grey, each piece is filled with a soft brand gradient (green → violet,
/// the DesignSystem primary/tertiary) that slowly drifts across the shape — a
/// modern, on-brand loading effect. Gated by Reduce Motion — when reduced, the
/// gradient is shown static (no drift). Instantiate `AuroraFill` directly,
/// sized by the piece it stands in for.
@available(iOS 17.0, macOS 14.0, *)
struct AuroraFill: View {
    var cornerRadius: CGFloat = 8

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var drift: CGFloat = -1

    private var gradient: LinearGradient {
        LinearGradient(
            colors: [
                DSColor.onSurface.opacity(0.10),
                DSColor.primary.opacity(0.28),
                DSColor.tertiary.opacity(0.26),
                DSColor.onSurface.opacity(0.10)
            ],
            startPoint: .leading,
            endPoint: .trailing
        )
    }

    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            RoundedRectangle(cornerRadius: cornerRadius)
                .fill(DSColor.onSurface.opacity(0.12))
                .overlay(
                    gradient
                        .frame(width: w * 1.8)
                        .offset(x: reduceMotion ? 0 : drift * w)
                        .blendMode(.plusLighter)
                )
                .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
        }
        .onAppear {
            guard !reduceMotion else { return }
            withAnimation(.easeInOut(duration: 1.8).repeatForever(autoreverses: true)) {
                drift = 0.4
            }
        }
    }
}

/// A staggered entrance for a collection of skeleton pieces: each item fades +
/// rises in with a small per-index delay, giving the load a lively feel.
/// No-op under Reduce Motion.
@available(iOS 17.0, macOS 14.0, *)
private struct StaggeredAppear: ViewModifier {
    let index: Int
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var shown = false

    func body(content: Content) -> some View {
        if reduceMotion {
            content
        } else {
            content
                .opacity(shown ? 1 : 0)
                .offset(y: shown ? 0 : 10)
                .onAppear {
                    withAnimation(.easeOut(duration: 0.4).delay(Double(index) * 0.06)) { shown = true }
                }
        }
    }
}

@available(iOS 17.0, macOS 14.0, *)
private extension View {
    func staggered(_ index: Int) -> some View { modifier(StaggeredAppear(index: index)) }
}

/// A skeleton placeholder shaped like a player TILE (hero band + two metric
/// rows + a CTA band), painted with the animated aurora fill. Matches the real
/// cards so the loading state previews the content that will appear.
@available(iOS 17.0, macOS 14.0, *)
struct SkeletonCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
            AuroraFill(cornerRadius: 18).frame(height: 112)
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
                AuroraFill(cornerRadius: 4).frame(width: 90, height: 18)
                HStack(spacing: DSSpacingSwiftUI.sm) {
                    AuroraFill(cornerRadius: 4).frame(width: 44, height: 12)
                    AuroraFill(cornerRadius: 4).frame(width: 44, height: 12)
                    AuroraFill(cornerRadius: 4).frame(width: 44, height: 12)
                }
            }
            .padding(.horizontal, DSSpacingSwiftUI.sm)
            AuroraFill(cornerRadius: 19).frame(height: 38)
                .padding(.horizontal, DSSpacingSwiftUI.sm)
                .padding(.bottom, DSSpacingSwiftUI.sm)
        }
        .frame(maxWidth: .infinity, alignment: .top)
        .background(skeletonSurface)
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(DSColor.primary.opacity(0.18), lineWidth: 1))
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .accessibilityHidden(true)
    }
}

/// A skeleton placeholder shaped like a Presupuesto TEAM ROW (`BudgetRow`:
/// team name + divider + SALDO/RENDIMIENTO + PUJA MÁXIMA/PREMIOS), full width.
/// Painted with the aurora fill; used by Presupuesto instead of the tile grid.
@available(iOS 17.0, macOS 14.0, *)
struct SkeletonRow: View {
    var body: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.md) {
            AuroraFill(cornerRadius: 6).frame(width: 150, height: 22)   // team name
            Divider().overlay(DSColor.onSurface.opacity(0.12))
            HStack(alignment: .top, spacing: DSSpacingSwiftUI.md) {
                metricColumn(alignment: .leading)
                metricColumn(alignment: .trailing)
            }
            HStack(alignment: .top, spacing: DSSpacingSwiftUI.md) {
                metricColumn(alignment: .leading)
                metricColumn(alignment: .trailing)
            }
        }
        .padding(DSSpacingSwiftUI.md)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(skeletonSurface)
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(DSColor.primary.opacity(0.18), lineWidth: 1))
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .accessibilityHidden(true)
    }

    private func metricColumn(alignment: HorizontalAlignment) -> some View {
        VStack(alignment: alignment, spacing: 6) {
            AuroraFill(cornerRadius: 3).frame(width: 60, height: 10)
            AuroraFill(cornerRadius: 4).frame(width: 90, height: 18)
        }
        .frame(maxWidth: .infinity, alignment: alignment == .trailing ? .trailing : .leading)
    }
}

/// Skeleton placeholder for the SUMMARY / BANNER card (Mercado/Presupuesto/
/// Calculadora show one above the list). A header band with the aurora fill.
@available(iOS 17.0, macOS 14.0, *)
struct SkeletonHeader: View {
    var height: CGFloat = 120

    var body: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
            AuroraFill(cornerRadius: 4).frame(width: 120, height: 20)
            HStack(spacing: DSSpacingSwiftUI.md) {
                AuroraFill(cornerRadius: 4).frame(height: 14)
                AuroraFill(cornerRadius: 4).frame(height: 14)
                AuroraFill(cornerRadius: 4).frame(height: 14)
            }
            Spacer(minLength: 0)
        }
        .padding(DSSpacingSwiftUI.md)
        .frame(height: height)
        .frame(maxWidth: .infinity, alignment: .topLeading)
        .background(skeletonSurface)
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(DSColor.primary.opacity(0.18), lineWidth: 1))
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .padding(.horizontal, DSSpacingSwiftUI.md)
        .accessibilityHidden(true)
    }
}

/// Shared glass surface for skeleton pieces (matches the real tiles/cards).
@available(iOS 17.0, macOS 14.0, *)
private var skeletonSurface: some View {
    RoundedRectangle(cornerRadius: 18)
        .fill(Color.black.opacity(0.5))
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
}

/// Loading view for TILE-GRID screens (Mercado/Calculadora/Favoritos): an
/// optional header band + a 2-up grid of aurora tiles, entering staggered,
/// inside a non-interactive ScrollView.
@available(iOS 17.0, macOS 14.0, *)
struct SkeletonScreen: View {
    var showHeader: Bool = true
    var cardCount: Int = 6

    var body: some View {
        ScrollView {
            VStack(spacing: DSSpacingSwiftUI.md) {
                if showHeader { SkeletonHeader().staggered(0) }
                LazyVGrid(
                    columns: [
                        GridItem(.flexible(), spacing: DSSpacingSwiftUI.md),
                        GridItem(.flexible(), spacing: DSSpacingSwiftUI.md)
                    ],
                    spacing: DSSpacingSwiftUI.md
                ) {
                    ForEach(0..<cardCount, id: \.self) { i in
                        SkeletonCard().staggered(i + 1)
                    }
                }
                .padding(.horizontal, DSSpacingSwiftUI.md)
            }
            .padding(.top, DSSpacingSwiftUI.md)
        }
        .allowsHitTesting(false)
        .accessibilityElement()
        .accessibilityLabel("Cargando")
    }
}

/// Loading view for ROW-LIST screens (Presupuesto): an optional header band +
/// a column of full-width aurora rows, entering staggered.
@available(iOS 17.0, macOS 14.0, *)
struct SkeletonListScreen: View {
    var showHeader: Bool = true
    var rowCount: Int = 5

    var body: some View {
        ScrollView {
            VStack(spacing: DSSpacingSwiftUI.md) {
                if showHeader { SkeletonHeader().staggered(0) }
                ForEach(0..<rowCount, id: \.self) { i in
                    SkeletonRow()
                        .padding(.horizontal, DSSpacingSwiftUI.md)
                        .staggered(i + 1)
                }
            }
            .padding(.top, DSSpacingSwiftUI.md)
        }
        .allowsHitTesting(false)
        .accessibilityElement()
        .accessibilityLabel("Cargando")
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
