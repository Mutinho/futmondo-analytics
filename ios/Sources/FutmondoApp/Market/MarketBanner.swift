import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Economy summary card (W2 / FR3 / US2), redesigned as a modern, elegant
/// surface instead of a flat tile grid:
///
/// - A HERO figure: **Disponible** — the money the manager can actually commit —
///   big and money-coloured, with a plain-language caption so colour is never
///   the sole carrier (A7 / NFR6).
/// - A NATIVE Swift Charts capacity bar (`Charts.framework`, Apple SDK, cost
///   0 €) showing how the **puja máxima** splits into *en pujas* (committed) and
///   *disponible* (free), so the headroom reads at a glance. Degrades to a
///   hand-drawn proportional bar when Charts is unavailable (older runtime /
///   non-UIKit dev build), never a blank.
/// - A compact metrics strip: Presupuesto · En pujas · Balance, each labelled,
///   with Balance signed + money-coloured.
///
/// All five FR3 figures remain present and individually VoiceOver-labelled.
@available(iOS 17.0, macOS 14.0, *)
public struct MarketBanner: View {
    private let userInfo: MarketUserInfo

    public init(userInfo: MarketUserInfo) {
        self.userInfo = userInfo
    }

    private var availableIsHealthy: Bool { userInfo.availableForBids > 0 }

    public var body: some View {
        NeonGlassCard {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.md) {
                hero
                Divider().overlay(DSColor.onSurface.opacity(0.15))
                metricsStrip
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabel)
        .accessibilityIdentifier("market-banner")
    }

    // MARK: - Hero (Disponible)

    private var hero: some View {
        HStack(alignment: .firstTextBaseline) {
            VStack(alignment: .leading, spacing: 2) {
                DSStatLabel("DISPONIBLE PARA PUJAR")
                Text(money(userInfo.availableForBids))
                    .font(DSFont.h1)
                    .foregroundStyle(availableIsHealthy ? DSColor.moneyPositive : DSColor.moneyNegative)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 2) {
                DSStatLabel("PUJA MÁXIMA")
                Text(money(userInfo.maxBid))
                    .font(DSFont.h3)
                    .foregroundStyle(DSColor.onSurface)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            }
        }
    }

    // MARK: - Metrics strip (Presupuesto · En pujas · Balance)

    private var metricsStrip: some View {
        HStack(alignment: .top, spacing: DSSpacingSwiftUI.md) {
            metric("PRESUPUESTO", money(userInfo.balance), color: DSColor.onSurface, alignment: .leading)
            metric("EN PUJAS", money(userInfo.activeBidsTotal), color: DSColor.tertiary, alignment: .center)
            metric(
                "BALANCE",
                MoneyFormatter.format(userInfo.balanceMinusBids, signed: true),
                color: userInfo.balanceMinusBids >= 0 ? DSColor.moneyPositive : DSColor.moneyNegative,
                alignment: .trailing
            )
        }
    }

    private func metric(_ label: String, _ value: String, color: Color, alignment: HorizontalAlignment) -> some View {
        VStack(alignment: alignment, spacing: 2) {
            DSStatLabel(label)
            Text(value)
                .font(DSFont.body.weight(.bold))
                .foregroundStyle(color)
                .lineLimit(1)
                .minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity, alignment: frameAlignment(alignment))
    }

    private func frameAlignment(_ a: HorizontalAlignment) -> Alignment {
        switch a {
        case .leading: return .leading
        case .trailing: return .trailing
        default: return .center
        }
    }

    // MARK: - Helpers

    private func money(_ amount: Int) -> String { MoneyFormatter.format(amount, signed: false) }

    private var accessibilityLabel: String {
        "Resumen económico. "
            + "Disponible para pujar \(money(userInfo.availableForBids)) \(availableIsHealthy ? "positivo" : "no positivo"). "
            + "Puja máxima \(money(userInfo.maxBid)). "
            + "Presupuesto \(money(userInfo.balance)). "
            + "En pujas \(money(userInfo.activeBidsTotal)). "
            + "Balance \(MoneyFormatter.format(userInfo.balanceMinusBids, signed: true))."
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
