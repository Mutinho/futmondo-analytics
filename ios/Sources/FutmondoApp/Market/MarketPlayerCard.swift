import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// A single market player TILE (V3 / FR4 / W3–W5), redesigned around a large
/// semi-transparent player HERO image that spans the tile width (you recognise
/// the player from half a face), with the name + team CREST + Sofascore rating
/// overlaid on top. The team NAME is dropped — the crest identifies it and we
/// win vertical space. Laid out two per row by `MarketView`.
///
/// Below the hero: a compact metric strip whose labels never wrap
/// (VALOR · SUG. · TEND., single-line), then the gradient "PUJAR" CTA (or the
/// active-bid footer with cancel). All Angular data preserved; the bid/cancel
/// split uses the corrected `activeBidAmount`.
@available(iOS 17.0, macOS 14.0, *)
public struct MarketPlayerCard: View {
    private let player: MarketPlayer
    private let isWriting: Bool
    private let onBid: () -> Void
    private let onCancel: () -> Void
    private let onOpenSofascore: () -> Void
    private let onOpenSofascoreProfile: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var pressed = false

    public init(
        player: MarketPlayer,
        isWriting: Bool,
        onBid: @escaping () -> Void,
        onCancel: @escaping () -> Void,
        onOpenSofascore: @escaping () -> Void,
        onOpenSofascoreProfile: @escaping () -> Void
    ) {
        self.player = player
        self.isWriting = isWriting
        self.onBid = onBid
        self.onCancel = onCancel
        self.onOpenSofascore = onOpenSofascore
        self.onOpenSofascoreProfile = onOpenSofascoreProfile
    }

    private var accent: Color { PositionChip.bandColor(for: player.position ?? "") }

    public var body: some View {
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
            color: glowColor.opacity(DSElevation.neonGlow.opacity),
            radius: DSElevation.neonGlow.radius,
            x: 0,
            y: DSElevation.neonGlow.y
        )
        .scaleEffect(pressed ? 0.97 : 1)
        .animation(reduceMotion ? nil : .spring(response: 0.3, dampingFraction: 0.7), value: pressed)
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("market-player-card-\(player.playerId)")
    }

    /// Neon halo colour: the DS green glow of the budget cards, or amber for a
    /// favourite (so the highlight reads as "favourite" rather than generic).
    private var glowColor: Color {
        player.isFavorite ? Color(red: 0.98, green: 0.75, blue: 0.14) : DSColor.primary
    }

    // MARK: - Hero image (rating label + floating overflow menu)

    private var hero: some View {
        heroContent
    }

    private var heroContent: some View {
        ZStack(alignment: .bottomLeading) {
            heroImage
                .frame(maxWidth: .infinity)
                .frame(height: 112)
                .clipped()

            // Bottom-up scrim so the overlaid name/crest stay legible over the
            // photo (the photo itself is already dimmed to ~0.55).
            LinearGradient(
                colors: [.clear, .black.opacity(0.75)],
                startPoint: .center,
                endPoint: .bottom
            )

            // Top-right cluster: favourite + position chip.
            VStack(alignment: .trailing, spacing: 4) {
                HStack(spacing: 4) {
                    if player.isFavorite { favoriteStar }
                    if let position = player.position, !position.isEmpty {
                        PositionChip(position: position)
                    }
                }
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topTrailing)
            .padding(6)

            // Top-left: Sofascore rating.
            sofascoreRatingLabel
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
                    image
                        .resizable()
                        .scaledToFill()
                        .opacity(0.55) // semi-transparent — half a face is enough
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

    /// Sofascore rating label (non-interactive; actions live in the overflow
    /// menu). Colour-banded by rating, with the numeric value present so meaning
    /// is not colour-only (A7).
    private var sofascoreRatingLabel: some View {
        Text(player.sofascoreRating.map { ratingText($0) } ?? "—")
            .font(.caption.weight(.heavy))
            .foregroundStyle(.white)
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(sofascoreColor(player.sofascoreRating), in: Capsule())
            .overlay(Capsule().stroke(.white.opacity(0.6), lineWidth: 1))
            .shadow(color: .black.opacity(0.4), radius: 2, y: 1)
            .accessibilityLabel("Rating Sofascore \(player.sofascoreRating.map { ratingText($0) } ?? "sin dato")")
    }

    @ViewBuilder
    private var favoriteStar: some View {
        let star = Image(systemName: "star.fill")
            .font(.caption)
            .foregroundStyle(Color(red: 0.98, green: 0.75, blue: 0.14))
            .shadow(color: .black.opacity(0.5), radius: 1)
            .accessibilityHidden(true)
        if #available(iOS 17.0, *) {
            star.symbolEffect(.bounce, value: player.playerId)
        } else {
            star
        }
    }

    // MARK: - Metrics: VALOR hero + PUNTOS, then compact secondary row

    private var metricStrip: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
            // Primary row: VALOR (hero) + PUNTOS — the two figures that drive
            // bidding power — given clear visual weight.
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

            // Secondary row: SUG. · TITULAR · TEND. (compact, never wrapping).
            HStack(alignment: .top, spacing: DSSpacingSwiftUI.xs) {
                miniMetric("SUG.", MoneyFormatter.format(player.suggestedBid, signed: false))
                if let pct = player.starterPct {
                    miniMetric("TITULAR", "\(pct)%")
                }
                trendMini
            }
        }
    }

    /// Points scored this season, or "-" when none. (Matches/jornadas omitted —
    /// the figure that matters for bidding is the points total.)
    private var pointsText: String {
        guard let points = player.points, points > 0 else { return "-" }
        return "\(points)"
    }

    private func miniMetric(_ label: String, _ value: String, accent: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: 1) {
            Text(label)
                .font(.system(size: 9, weight: .heavy))
                .foregroundStyle(accent ? DSColor.primary : DSColor.onSurfaceVariant)
                .lineLimit(1)
                .fixedSize()                      // never wrap the label
            Text(value)
                .font(.caption.weight(accent ? .heavy : .semibold))
                .foregroundStyle(accent ? DSColor.primary : DSColor.onSurface)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    @ViewBuilder
    private var trendMini: some View {
        VStack(alignment: .leading, spacing: 1) {
            Text("TEND.")
                .font(.system(size: 9, weight: .heavy))
                .foregroundStyle(DSColor.onSurfaceVariant)
                .lineLimit(1)
                .fixedSize()
            if let change = player.change {
                let up = change >= 0
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
                Text("-").font(.caption.weight(.semibold)).foregroundStyle(DSColor.onSurface)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    // MARK: - Footer (tap-to-bid CTA, or active-bid + cancel)

    @ViewBuilder
    private var footer: some View {
        if let activeBid = player.activeBidAmount {
            HStack(spacing: DSSpacingSwiftUI.xs) {
                Image(systemName: "tag.fill").font(.caption2).foregroundStyle(DSColor.tertiary)
                    .accessibilityHidden(true)
                Text(MoneyFormatter.format(activeBid, signed: false))
                    .font(.caption.weight(.bold))
                    .foregroundStyle(DSColor.tertiary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
                Spacer(minLength: DSSpacingSwiftUI.xs)
                Button(role: .destructive, action: onCancel) {
                    Image(systemName: "xmark")
                        .font(.footnote.weight(.bold))
                        .foregroundStyle(DSColor.moneyNegative)
                        .frame(width: 34, height: 34)
                        .background(DSColor.moneyNegative.opacity(0.12), in: Circle())
                }
                .buttonStyle(.plain)
                .disabled(isWriting)
                .accessibilityLabel("Cancelar puja de \(player.name)")
                .accessibilityIdentifier("market-cancel-\(player.playerId)")
                roundMenuButton
            }
            .padding(.horizontal, DSSpacingSwiftUI.sm)
            .padding(.vertical, 6)
            .frame(maxWidth: .infinity)
            .background(DSColor.tertiary.opacity(0.12), in: RoundedRectangle(cornerRadius: 14))
        } else {
            HStack(spacing: DSSpacingSwiftUI.xs) {
                BidCTA(
                    isEnabled: !isWriting,
                    pressed: $pressed,
                    action: onBid
                )
                .accessibilityLabel("Pujar por \(player.name), sugerida \(MoneyFormatter.format(player.suggestedBid, signed: false))")
                .accessibilityIdentifier("market-bid-\(player.playerId)")
                roundMenuButton
            }
        }
    }

    /// Round "…" action button next to PUJAR: a clear, tappable glass circle
    /// whose menu holds the player actions (stats / Sofascore profile).
    private var roundMenuButton: some View {
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
        .accessibilityIdentifier("market-more-\(player.playerId)")
    }

    // MARK: - Surface / border

    private var tileSurface: some View {
        RoundedRectangle(cornerRadius: 18)
            .fill(Color.black.opacity(0.5))
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }

    private var tileBorder: some View {
        RoundedRectangle(cornerRadius: 18)
            .stroke(
                player.isFavorite
                    ? Color(red: 0.98, green: 0.75, blue: 0.14)
                    : accent.opacity(0.35),
                lineWidth: player.isFavorite ? 2 : 1
            )
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

// MARK: - Modern gradient CTA

@available(iOS 17.0, macOS 14.0, *)
private struct BidCTA: View {
    let isEnabled: Bool
    @Binding var pressed: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 5) {
                Image(systemName: "hammer.fill").font(.caption2).accessibilityHidden(true)
                Text("PUJAR")
                    .font(.caption.weight(.heavy))
                    .lineLimit(1)
            }
            .foregroundStyle(DSColor.onPrimary)
            .frame(maxWidth: .infinity, minHeight: 38)
            .background(DSColor.primary, in: Capsule())
        }
        .buttonStyle(PressReportingStyle(pressed: $pressed))
        .disabled(!isEnabled)
        .opacity(isEnabled ? 1 : 0.5)
    }
}

@available(iOS 17.0, macOS 14.0, *)
private struct PressReportingStyle: ButtonStyle {
    @Binding var pressed: Bool
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .onChange(of: configuration.isPressed) { _, now in pressed = now }
    }
}

// MARK: - Team crest / position chip (shared across the market screen)

/// Team crest loaded from the Angular `teams/64/{team_logo}` base; a neutral
/// placeholder circle when there is no logo value.
@available(iOS 17.0, macOS 14.0, *)
struct TeamLogo: View {
    let logo: String?
    let team: String
    var size: CGFloat = 22

    var body: some View {
        Group {
            if let url = MarketImageURL.teamLogo(logo) {
                AsyncImage(url: url) { phase in
                    if case .success(let image) = phase {
                        image.resizable().scaledToFit()
                    } else {
                        Circle().fill(.white.opacity(0.15))
                    }
                }
            } else {
                Circle().fill(.white.opacity(0.15))
            }
        }
        .frame(width: size, height: size)
        .accessibilityLabel("Equipo \(team)")
    }
}

/// A small position chip reproducing the Angular `.pos-chip` colour bands
/// (fwd/mid/def/gk) with a short uppercase label (DL/MC/DF/PT).
@available(iOS 17.0, macOS 14.0, *)
struct PositionChip: View {
    let position: String

    var body: some View {
        Text(shortLabel)
            .font(.system(size: 10, weight: .heavy))
            .foregroundStyle(.black.opacity(0.85))
            .padding(.horizontal, 7)
            .padding(.vertical, 2)
            .background(PositionChip.bandColor(for: position))
            .clipShape(Capsule())
            .fixedSize()
            .accessibilityLabel("Posición \(position)")
    }

    private var shortLabel: String {
        let p = position.lowercased()
        if p.contains("delantero") || p.contains("forward") { return "DL" }
        if p.contains("defensa") || p.contains("defender") { return "DF" }
        if p.contains("portero") || p.contains("keeper") || p.contains("gk") { return "PT" }
        if p.contains("centrocampista") || p.contains("medio") || p.contains("mid") { return "MC" }
        return position.uppercased()
    }

    static func bandColor(for position: String) -> Color {
        let p = position.lowercased()
        if p.contains("delantero") || p.contains("forward") {
            return Color(red: 0.90, green: 0.45, blue: 0.45) // #e57373
        }
        if p.contains("defensa") || p.contains("defender") {
            return Color(red: 1.00, green: 0.72, blue: 0.30) // #ffb74d
        }
        if p.contains("portero") || p.contains("keeper") || p.contains("gk") {
            return Color(red: 0.30, green: 0.69, blue: 0.31) // #4caf50
        }
        return Color(red: 0.39, green: 0.71, blue: 0.96) // #64b5f6 (mid/default)
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
