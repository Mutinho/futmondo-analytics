import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// A single favourite player TILE (V1 / FR3 / W4–W5), reusing the Mercado card
/// aesthetic (large semi-transparent player HERO image spanning the tile width,
/// name + team CREST + Sofascore rating overlaid on top), laid out two per row
/// by `FavoritesView`.
///
/// Below the hero: a compact metric strip (VALOR · PUNTOS, then TITULAR · TEND.
/// · MEDIA), then a destructive "QUITAR" CTA beside the "…" overflow menu
/// (Sofascore estadísticas / perfil). Null/zero figures render "-" per BR3.1;
/// the media line carries home/away/matches secondary text per BR3.2; the badge
/// uses `sofascoreRating` (NOT `rating`) per BR3.3.
@available(iOS 17.0, macOS 14.0, *)
struct FavoritePlayerCard: View {
    private let player: FavoritePlayer
    private let isWriting: Bool
    private let onRemove: () -> Void
    private let onOpenSofascore: () -> Void
    private let onOpenSofascoreProfile: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    init(
        player: FavoritePlayer,
        isWriting: Bool,
        onRemove: @escaping () -> Void,
        onOpenSofascore: @escaping () -> Void,
        onOpenSofascoreProfile: @escaping () -> Void
    ) {
        self.player = player
        self.isWriting = isWriting
        self.onRemove = onRemove
        self.onOpenSofascore = onOpenSofascore
        self.onOpenSofascoreProfile = onOpenSofascoreProfile
    }

    private var accent: Color { PositionChip.bandColor(for: player.position ?? "") }

    var body: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
            hero
            metricStrip
                .padding(.horizontal, DSSpacingSwiftUI.sm)
            footer
                .padding(.horizontal, DSSpacingSwiftUI.sm)
                .padding(.bottom, DSSpacingSwiftUI.sm)
        }
        .frame(maxWidth: .infinity, alignment: .top)
        .background(tileSurface)
        .overlay(tileBorder)
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .shadow(
            color: DSColor.primary.opacity(DSElevation.neonGlow.opacity),
            radius: DSElevation.neonGlow.radius,
            x: 0,
            y: DSElevation.neonGlow.y
        )
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("favorite-player-card-\(player.playerId)")
    }

    // MARK: - Hero image (rating badge + name + crest overlay)

    private var hero: some View {
        ZStack(alignment: .bottomLeading) {
            heroImage
                .frame(maxWidth: .infinity)
                .frame(height: 112)
                .clipped()

            LinearGradient(
                colors: [.clear, .black.opacity(0.75)],
                startPoint: .center,
                endPoint: .bottom
            )

            // Top-right: position chip.
            VStack(alignment: .trailing) {
                if let position = player.position, !position.isEmpty {
                    PositionChip(position: position)
                }
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topTrailing)
            .padding(6)

            // Top-left: Sofascore rating badge (BR3.3 — uses sofascoreRating).
            sofascoreRatingBadge
                .padding(6)
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)

            // Bottom overlay: name + team crest (team NAME intentionally dropped).
            HStack(alignment: .center, spacing: 6) {
                TeamLogo(logo: player.teamLogo, team: player.team)
                Text(player.name)
                    .font(DSFont.h3)
                    .foregroundStyle(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
                    .shadow(color: .black.opacity(0.6), radius: 2, y: 1)
                Spacer(minLength: 0)
            }
            .padding(.horizontal, DSSpacingSwiftUI.sm)
            .padding(.bottom, 6)
        }
        .frame(height: 112)
        .clipShape(.rect(topLeadingRadius: 18, topTrailingRadius: 18))
    }

    @ViewBuilder
    private var heroImage: some View {
        if let url = MarketImageURL.playerPhoto(slug: player.slug) {
            AsyncImage(url: url) { phase in
                switch phase {
                case .success(let image):
                    image.resizable().scaledToFill().opacity(0.55)
                default:
                    heroFallback
                }
            }
        } else {
            heroFallback
        }
    }

    private var heroFallback: some View {
        ZStack {
            accent.opacity(0.25)
            Image(systemName: "person.fill")
                .font(.system(size: 48))
                .foregroundStyle(.white.opacity(0.4))
        }
        .frame(maxWidth: .infinity)
    }

    /// Sofascore rating badge (BR3.3): the `sofascoreRating` value, colour-banded,
    /// with "-" when absent (BR3.1). The numeric value is present so meaning is
    /// not colour-only (A7).
    private var sofascoreRatingBadge: some View {
        Text(player.sofascoreRating.map { ratingText($0) } ?? "-")
            .font(.caption.weight(.heavy))
            .foregroundStyle(.white)
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(sofascoreColor(player.sofascoreRating), in: Capsule())
            .overlay(Capsule().stroke(.white.opacity(0.6), lineWidth: 1))
            .shadow(color: .black.opacity(0.4), radius: 2, y: 1)
            .accessibilityLabel("Rating Sofascore \(player.sofascoreRating.map { ratingText($0) } ?? "sin dato")")
    }

    // MARK: - Metrics

    private var metricStrip: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
            // Primary row: VALOR + PUNTOS.
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 0) {
                    Text("VALOR")
                        .font(.system(size: 9, weight: .heavy))
                        .foregroundStyle(DSColor.onSurfaceVariant)
                        .lineLimit(1)
                        .fixedSize()
                    Text(MoneyFormatter.format(player.value, signed: false))
                        .font(.title3.weight(.heavy))
                        .foregroundStyle(DSColor.onSurface)
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                }
                Spacer(minLength: DSSpacingSwiftUI.xs)
                VStack(alignment: .trailing, spacing: 0) {
                    Text("PUNTOS")
                        .font(.system(size: 9, weight: .heavy))
                        .foregroundStyle(DSColor.onSurfaceVariant)
                        .lineLimit(1)
                        .fixedSize()
                    Text(pointsText)
                        .font(.title3.weight(.heavy))
                        .foregroundStyle(DSColor.primary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                }
            }

            // Secondary row: TITULAR · TEND. · MEDIA (compact, never wrapping).
            HStack(alignment: .top, spacing: DSSpacingSwiftUI.xs) {
                starterMini
                trendMini
                averageMini
            }
        }
    }

    /// Points, or "-" when null/zero (BR3.1 — 0 renders "-" like the web).
    private var pointsText: String {
        guard let points = player.points, points > 0 else { return "-" }
        return "\(points)"
    }

    @ViewBuilder
    private var starterMini: some View {
        miniContainer("TITULAR") {
            if let pct = player.starterPct {
                Text("\(pct)%")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(DSColor.onSurface)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
            } else {
                dash
            }
        }
    }

    /// Trend: arrow + colour when change != 0; "-" when null OR exactly 0
    /// (BR3.1 — `@if p.change !== 0` in the web; 0 has no arrow).
    @ViewBuilder
    private var trendMini: some View {
        miniContainer("TEND.") {
            if let change = player.change, change != 0 {
                let up = change > 0
                HStack(spacing: 1) {
                    Image(systemName: up ? "arrow.up" : "arrow.down")
                        .font(.system(size: 9, weight: .bold))
                        .accessibilityHidden(true)
                    Text(MoneyFormatter.format(change, signed: true))
                        .font(.caption.weight(.semibold))
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                }
                .foregroundStyle(up ? DSColor.moneyPositive : DSColor.moneyNegative)
            } else {
                dash
            }
        }
    }

    /// Media: the season average, with home/away/matches as a secondary line
    /// (BR3.2). "-" when the average is null or zero (BR3.1).
    @ViewBuilder
    private var averageMini: some View {
        miniContainer("MEDIA") {
            if let average = player.average, average > 0 {
                VStack(alignment: .leading, spacing: 0) {
                    Text(ratingText(average))
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(DSColor.onSurface)
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                    if let secondary = mediaSecondaryText {
                        Text(secondary)
                            .font(.system(size: 8, weight: .semibold))
                            .foregroundStyle(DSColor.onSurfaceVariant)
                            .lineLimit(1)
                            .minimumScaleFactor(0.6)
                            .accessibilityLabel(mediaSecondaryAccessibility ?? secondary)
                    }
                }
            } else {
                dash
            }
        }
    }

    /// Secondary media line: "C 7.9 · F 6.8 · 18j" with only the present parts
    /// (BR3.2). Returns nil when none of home/away/matches is available.
    private var mediaSecondaryText: String? {
        var parts: [String] = []
        if let home = player.homeAverage, home > 0 { parts.append("C \(ratingText(home))") }
        if let away = player.awayAverage, away > 0 { parts.append("F \(ratingText(away))") }
        if let matches = player.matches, matches > 0 { parts.append("\(matches)j") }
        return parts.isEmpty ? nil : parts.joined(separator: " · ")
    }

    private var mediaSecondaryAccessibility: String? {
        var parts: [String] = []
        if let home = player.homeAverage, home > 0 { parts.append("media en casa \(ratingText(home))") }
        if let away = player.awayAverage, away > 0 { parts.append("media fuera \(ratingText(away))") }
        if let matches = player.matches, matches > 0 { parts.append("\(matches) partidos") }
        return parts.isEmpty ? nil : parts.joined(separator: ", ")
    }

    private var dash: some View {
        Text("-").font(.caption.weight(.semibold)).foregroundStyle(DSColor.onSurface)
    }

    private func miniContainer<Content: View>(
        _ label: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: 1) {
            Text(label)
                .font(.system(size: 9, weight: .heavy))
                .foregroundStyle(DSColor.onSurfaceVariant)
                .lineLimit(1)
                .fixedSize()
            content()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    // MARK: - Footer (QUITAR CTA + overflow menu)

    private var footer: some View {
        HStack(spacing: DSSpacingSwiftUI.xs) {
            Button(role: .destructive, action: onRemove) {
                HStack(spacing: 5) {
                    Image(systemName: "star.slash.fill").font(.caption2).accessibilityHidden(true)
                    Text("QUITAR")
                        .font(.caption.weight(.heavy))
                        .lineLimit(1)
                }
                .foregroundStyle(DSColor.onPrimary)
                .frame(maxWidth: .infinity, minHeight: 38)
                .background(DSColor.moneyNegative, in: Capsule())
            }
            .buttonStyle(.plain)
            .disabled(isWriting)
            .opacity(isWriting ? 0.5 : 1)
            .accessibilityLabel("Quitar \(player.name) de favoritos")
            .accessibilityIdentifier("favorite-remove-\(player.playerId)")
            overflowMenu
        }
    }

    /// Round "…" action button: a menu with Sofascore estadísticas (always) and
    /// perfil (only when a URL exists — BR6.1).
    private var overflowMenu: some View {
        Menu {
            Button {
                onOpenSofascore()
            } label: {
                Label("Ver estadísticas", systemImage: "chart.bar.doc.horizontal")
            }
            if let url = player.sofascoreUrl, !url.isEmpty {
                Button {
                    onOpenSofascoreProfile()
                } label: {
                    Label("Ver perfil Sofascore", systemImage: "safari")
                }
            }
        } label: {
            Image(systemName: "ellipsis")
                .font(.system(size: 15, weight: .bold))
                .foregroundStyle(DSColor.onSurface)
                .frame(width: 38, height: 38)
                .background(DSColor.onSurface.opacity(0.1), in: Circle())
                .overlay(Circle().stroke(DSColor.onSurface.opacity(0.2), lineWidth: 1))
        }
        .accessibilityLabel("Más opciones de \(player.name)")
        .accessibilityIdentifier("favorite-more-\(player.playerId)")
    }

    // MARK: - Surface / border

    private var tileSurface: some View {
        RoundedRectangle(cornerRadius: 18)
            .fill(Color.black.opacity(0.5))
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }

    private var tileBorder: some View {
        RoundedRectangle(cornerRadius: 18)
            .stroke(accent.opacity(0.35), lineWidth: 1)
    }

    // MARK: - Helpers

    private func ratingText(_ value: Double) -> String { String(format: "%.1f", value) }

    private func sofascoreColor(_ rating: Double?) -> Color {
        guard let rating else { return DSColor.onSurfaceVariant }
        if rating >= 7.0 { return DSColor.moneyPositive }
        if rating >= 6.0 { return DSColor.moneyPrize }
        return DSColor.moneyNegative
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
