import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// A single selectable roster TILE for the Calculadora (FR5.1 / FR6.1),
/// reusing the Mercado card aesthetic (hero photo, glass/neon surface, position
/// chip, crest) with the Calculadora content: VALOR ACTUAL, TENDENCIA, VALOR
/// PROYECTADO and PLUSVALÍA. A tap toggles selection; the selected state shows a
/// check overlay and a green ring (selection is NOT colour-only — the check icon
/// carries it, A7). Laid out two per row by `CalculatorView`.
@available(iOS 17.0, macOS 14.0, *)
struct CalculatorPlayerCard: View {
    let player: RosterPlayer
    let projectedValue: Int
    let daysAhead: Int
    let isSelected: Bool
    let onTap: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private var accent: Color { PositionChip.bandColor(for: player.position ?? "") }
    private var ringColor: Color { isSelected ? DSColor.primary : accent.opacity(0.35) }

    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
                hero
                metricStrip
                    .padding(.horizontal, DSSpacingSwiftUI.sm)
                    .padding(.bottom, DSSpacingSwiftUI.sm)
            }
            .frame(maxWidth: .infinity, alignment: .top)
            .background(tileSurface)
            .overlay(tileBorder)
            .clipShape(RoundedRectangle(cornerRadius: 18))
            .shadow(
                color: (isSelected ? DSColor.primary : DSColor.primary.opacity(0.4))
                    .opacity(DSElevation.neonGlow.opacity),
                radius: DSElevation.neonGlow.radius,
                x: 0,
                y: DSElevation.neonGlow.y
            )
        }
        .buttonStyle(.plain)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabel)
        .accessibilityAddTraits(isSelected ? [.isSelected, .isButton] : [.isButton])
        .accessibilityIdentifier("calculator-player-card-\(player.playerId)")
    }

    // MARK: - Hero (photo + name + crest + selection check)

    private var hero: some View {
        ZStack(alignment: .bottomLeading) {
            heroImage
                .frame(maxWidth: .infinity)
                .frame(height: 100)
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

            // Top-left: selection check (icon carries the state, not colour).
            VStack {
                selectionBadge
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            .padding(6)

            // Bottom overlay: crest + name.
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
        .frame(height: 100)
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
                .font(.system(size: 44))
                .foregroundStyle(.white.opacity(0.4))
        }
        .frame(maxWidth: .infinity)
    }

    private var selectionBadge: some View {
        Image(systemName: isSelected ? "checkmark.circle.fill" : "circle")
            .font(.system(size: 20, weight: .bold))
            .foregroundStyle(isSelected ? DSColor.primary : .white.opacity(0.8))
            .shadow(color: .black.opacity(0.5), radius: 2, y: 1)
            .accessibilityHidden(true)
    }

    // MARK: - Metrics (VALOR · TEND. / PROYECTADO · PLUSVALÍA)

    private var metricStrip: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
            HStack(alignment: .firstTextBaseline) {
                metric("VALOR", MoneyFormatter.format(player.value, signed: false), color: DSColor.onSurface, alignment: .leading)
                trendMetric
            }
            HStack(alignment: .firstTextBaseline) {
                metric(
                    daysAhead > 0 ? "PROYECTADO" : "HOY",
                    MoneyFormatter.format(projectedValue, signed: false),
                    color: DSColor.primary,
                    alignment: .leading
                )
                plusvaliaMetric
            }
        }
    }

    private func metric(_ label: String, _ value: String, color: Color, alignment: HorizontalAlignment) -> some View {
        VStack(alignment: alignment, spacing: 0) {
            Text(label)
                .font(.system(size: 9, weight: .heavy))
                .foregroundStyle(DSColor.onSurfaceVariant)
                .lineLimit(1)
                .fixedSize()
            Text(value)
                .font(.subheadline.weight(.heavy))
                .foregroundStyle(color)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
        }
        .frame(maxWidth: .infinity, alignment: alignment == .trailing ? .trailing : .leading)
    }

    @ViewBuilder
    private var trendMetric: some View {
        VStack(alignment: .trailing, spacing: 0) {
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
        .frame(maxWidth: .infinity, alignment: .trailing)
    }

    @ViewBuilder
    private var plusvaliaMetric: some View {
        VStack(alignment: .trailing, spacing: 0) {
            Text("PLUSVALÍA")
                .font(.system(size: 9, weight: .heavy))
                .foregroundStyle(DSColor.onSurfaceVariant)
                .lineLimit(1)
                .fixedSize()
            if let profit = player.profit {
                // Presentation-only sign + colour (BR7.1 / R-03).
                Text(MoneyFormatter.format(profit, signed: true))
                    .font(.caption.weight(.heavy))
                    .foregroundStyle(profit >= 0 ? DSColor.moneyPositive : DSColor.moneyNegative)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
            } else {
                Text("-").font(.caption.weight(.semibold)).foregroundStyle(DSColor.onSurface)
            }
        }
        .frame(maxWidth: .infinity, alignment: .trailing)
    }

    // MARK: - Surface / border

    private var tileSurface: some View {
        RoundedRectangle(cornerRadius: 18)
            .fill(Color.black.opacity(0.5))
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }

    private var tileBorder: some View {
        RoundedRectangle(cornerRadius: 18)
            .stroke(ringColor, lineWidth: isSelected ? 2 : 1)
    }

    private var accessibilityLabel: String {
        var parts = ["\(player.name).", "Valor \(MoneyFormatter.format(player.value, signed: false))."]
        if daysAhead > 0 {
            parts.append("Proyectado \(MoneyFormatter.format(projectedValue, signed: false)).")
        }
        if let profit = player.profit {
            parts.append("Plusvalía \(MoneyFormatter.format(profit, signed: true)).")
        }
        parts.append(isSelected ? "Seleccionado." : "No seleccionado.")
        return parts.joined(separator: " ")
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
