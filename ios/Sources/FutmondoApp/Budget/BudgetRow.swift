import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// A single team's budget row rendered as an ELEVATED CARD (D1), reproducing
/// the Angular `.team-card` cards view: a raised rounded surface with a soft
/// shadow, the team name as a header, `balance`/`performance` prominent on the
/// primary row (performance as a tinted BADGE), and `max_bid`/`prizes` on a
/// secondary row with small UPPERCASE labels (`SALDO` / `RENDIMIENTO` /
/// `PUJA MÁXIMA` / `PREMIOS`), exactly like the web. [FR1.2, FR1.3 / NFR5]
///
/// `performance` is rendered signed (`+`/`-`) via `MoneyFormatter.format(signed:)`;
/// `prizes` shows `-` when zero.
///
/// Accessibility: the card is a single VoiceOver element with a composite
/// label, and colour is never the sole carrier of meaning — the sign is always
/// present in the money strings (A7 / NFR5).
@available(iOS 15.0, macOS 12.0, *)
public struct BudgetRow: View {
    private let team: TeamBudget

    public init(team: TeamBudget) {
        self.team = team
    }

    // MARK: - Derived money strings (single source for label + display)

    private var balanceText: String { MoneyFormatter.format(team.balance, signed: false) }
    private var performanceText: String { MoneyFormatter.format(team.performance, signed: true) }
    private var maxBidText: String { MoneyFormatter.format(team.maxBid, signed: false) }
    private var prizesText: String {
        team.prizes == 0 ? "-" : MoneyFormatter.format(team.prizes, signed: false)
    }

    /// Money token color driven by the value sign (color is an *additional*
    /// carrier; the sign in the string is the primary one, A7).
    private func moneyColor(_ amount: Int) -> Color {
        amount < 0 ? DSColor.moneyNegative : DSColor.moneyPositive
    }

    public var body: some View {
        NeonGlassCard {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.md) {
                // Header: team name (large, h3) in WHITE over the dark glass.
                Text(team.teamName)
                    .font(DSFont.h3)
                    .foregroundStyle(DSColor.onSurface)
                    .padding(.bottom, DSSpacingSwiftUI.xs)

                // Subtle divider under the team name (matches the reference).
                Divider()
                    .overlay(DSColor.onSurface.opacity(0.15))

                // Primary row: SALDO (money color) + RENDIMIENTO (badge).
                HStack(alignment: .top, spacing: DSSpacingSwiftUI.md) {
                    VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
                        DSStatLabel("SALDO")
                        Text(balanceText)
                            .font(DSFont.h3)
                            .foregroundStyle(moneyColor(team.balance))
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)

                    VStack(alignment: .trailing, spacing: DSSpacingSwiftUI.xs) {
                        DSStatLabel("RENDIMIENTO")
                        DSMoneyBadge(value: performanceText, isNegative: team.performance < 0)
                    }
                    .frame(maxWidth: .infinity, alignment: .trailing)
                }

                // Secondary row: PUJA MÁXIMA (white) + PREMIOS (blue).
                HStack(alignment: .top, spacing: DSSpacingSwiftUI.md) {
                    secondaryMetric(
                        title: "PUJA MÁXIMA",
                        value: maxBidText,
                        color: DSColor.onSurface,
                        alignment: .leading
                    )
                    secondaryMetric(
                        title: "PREMIOS",
                        value: prizesText,
                        color: DSColor.moneyPrize,
                        alignment: .trailing
                    )
                }
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityLabel)
    }

    // MARK: - Subviews

    private func secondaryMetric(
        title: String,
        value: String,
        color: Color,
        alignment: HorizontalAlignment
    ) -> some View {
        VStack(alignment: alignment, spacing: DSSpacingSwiftUI.xs) {
            DSStatLabel(title)
            Text(value)
                .font(DSFont.body)
                .foregroundStyle(color)
        }
        .frame(maxWidth: .infinity, alignment: alignment == .leading ? .leading : .trailing)
    }

    // MARK: - Accessibility

    /// Composite VoiceOver label (accessibility-checklist):
    /// "Equipo <nombre>, saldo <valor> <positivo|negativo>, rendimiento <valor>,
    /// puja máxima <valor>, premios <valor|ninguno>".
    private var accessibilityLabel: String {
        let balanceSign = team.balance < 0 ? "negativo" : "positivo"
        let performanceSign = team.performance < 0 ? "negativo" : "positivo"
        let prizesSpoken = team.prizes == 0 ? "ninguno" : prizesText
        return "Equipo \(team.teamName), "
            + "saldo \(balanceText) \(balanceSign), "
            + "rendimiento \(performanceText) \(performanceSign), "
            + "puja máxima \(maxBidText), "
            + "premios \(prizesSpoken)"
    }
}

#endif // canImport(SwiftUI)
