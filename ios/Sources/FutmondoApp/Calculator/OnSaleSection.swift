import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// The "En venta" section of the Calculadora (FR9 / BR6.1). Shown only when the
/// toggle is ON and there is at least one on-sale player; the header's "En
/// venta" FIGURE stays visible regardless (BR6.1).
///
/// Presented as a **horizontal carousel** of compact tiles (`OnSaleCard`)
/// instead of full-width rows: a player photo hero, name, current price, and an
/// elegant native "Quitar" chip that asks `CalculatorView` for a confirmation
/// before cancelling the sale (W6).
@available(iOS 17.0, macOS 14.0, *)
struct OnSaleSection: View {
    let players: [OnSalePlayer]
    let isWriting: Bool
    let onCancel: (OnSalePlayer) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
            Text("EN VENTA (\(players.count))")
                .font(.caption.weight(.heavy))
                .foregroundStyle(DSColor.onSurfaceVariant)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: DSSpacingSwiftUI.sm) {
                    ForEach(players) { player in
                        OnSaleCard(
                            player: player,
                            isWriting: isWriting,
                            onCancel: { onCancel(player) }
                        )
                    }
                }
                .padding(.horizontal, 2)
                .padding(.vertical, 2)
            }
            // Let the carousel bleed to the screen edges for a native feel,
            // cancelling the parent's horizontal padding.
            .padding(.horizontal, -DSSpacingSwiftUI.md)
            .padding(.horizontal, DSSpacingSwiftUI.md)
        }
        .accessibilityIdentifier("calculator-on-sale-section")
    }
}

/// A compact on-sale tile (W6): player face hero, name, current price, and a
/// "Quitar" chip to remove it from the market. Reuses `MarketImageURL` for the
/// face, matching the Mercado aesthetic; a fixed width makes the carousel feel
/// deliberate.
@available(iOS 17.0, macOS 14.0, *)
struct OnSaleCard: View {
    let player: OnSalePlayer
    let isWriting: Bool
    let onCancel: () -> Void

    var body: some View {
        VStack(spacing: DSSpacingSwiftUI.xs) {
            face
            Text(player.name)
                .font(.footnote.weight(.semibold))
                .foregroundStyle(DSColor.onSurface)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
                .frame(maxWidth: .infinity)

            VStack(spacing: 0) {
                Text("PRECIO ACTUAL")
                    .font(.system(size: 8, weight: .heavy))
                    .foregroundStyle(DSColor.onSurfaceVariant)
                Text(MoneyFormatter.format(player.value, signed: false))
                    .font(.caption.weight(.bold))
                    .foregroundStyle(DSColor.tertiary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            }

            Button(role: .destructive, action: onCancel) {
                HStack(spacing: 4) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.caption2)
                        .accessibilityHidden(true)
                    Text("Quitar")
                        .font(.caption2.weight(.bold))
                }
                .foregroundStyle(DSColor.moneyNegative)
                .padding(.horizontal, DSSpacingSwiftUI.sm)
                .padding(.vertical, 5)
                .frame(maxWidth: .infinity)
                .background(DSColor.moneyNegative.opacity(0.14), in: Capsule())
            }
            .buttonStyle(.plain)
            .disabled(isWriting)
            .accessibilityLabel("Quitar de la venta a \(player.name)")
            .accessibilityIdentifier("calculator-cancel-\(player.playerId)")
        }
        .padding(DSSpacingSwiftUI.sm)
        .frame(width: 128)
        .background(Color.black.opacity(0.35), in: RoundedRectangle(cornerRadius: 16))
        .overlay(RoundedRectangle(cornerRadius: 16).stroke(DSColor.tertiary.opacity(0.35), lineWidth: 1))
        .accessibilityElement(children: .combine)
    }

    @ViewBuilder
    private var face: some View {
        if let url = MarketImageURL.playerPhoto(slug: player.slug) {
            AsyncImage(url: url) { phase in
                if case .success(let image) = phase {
                    image.resizable().scaledToFill()
                } else {
                    faceFallback
                }
            }
            .frame(width: 56, height: 56)
            .clipShape(Circle())
            .overlay(Circle().stroke(DSColor.tertiary.opacity(0.4), lineWidth: 1))
        } else {
            faceFallback
        }
    }

    private var faceFallback: some View {
        ZStack {
            Circle().fill(.white.opacity(0.15))
            Image(systemName: "person.fill")
                .font(.system(size: 24))
                .foregroundStyle(.white.opacity(0.4))
        }
        .frame(width: 56, height: 56)
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
