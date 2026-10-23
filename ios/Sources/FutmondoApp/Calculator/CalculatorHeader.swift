import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Economy summary header of the Calculadora (FR2 / BR6). A dark neon-glass
/// card (reusing `NeonGlassCard`, like the Mercado banner) showing: Saldo
/// actual, En venta (always, BR6.1), Pujas activas (N) only when N>0 (BR6.2),
/// Seleccionadas, and Saldo futuro — plus the "Incorporar jugadores en venta"
/// toggle. Money figures are paired with labels so meaning is never
/// colour-only (A7 / NFR6).
@available(iOS 17.0, macOS 14.0, *)
struct CalculatorHeader: View {
    let balance: Int
    let onSaleTotal: Int
    let activeBidsTotal: Int
    let activeBidsCount: Int
    let selectedTotal: Int
    let futureBalance: Int
    let includeOnSale: Bool
    let onToggleIncludeOnSale: (Bool) -> Void

    var body: some View {
        NeonGlassCard {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.md) {
                hero
                Divider().overlay(DSColor.onSurface.opacity(0.15))
                figuresStrip
                Divider().overlay(DSColor.onSurface.opacity(0.15))
                includeToggle
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabel)
        .accessibilityIdentifier("calculator-header")
    }

    // MARK: - Hero: Saldo futuro (the headline figure)

    private var hero: some View {
        HStack(alignment: .firstTextBaseline) {
            VStack(alignment: .leading, spacing: 2) {
                DSStatLabel("SALDO FUTURO")
                Text(MoneyFormatter.format(futureBalance, signed: true))
                    .font(DSFont.h1)
                    .foregroundStyle(futureBalance >= 0 ? DSColor.moneyPositive : DSColor.moneyNegative)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 2) {
                DSStatLabel("SALDO ACTUAL")
                Text(money(balance))
                    .font(DSFont.h3)
                    .foregroundStyle(balance >= 0 ? DSColor.onSurface : DSColor.moneyNegative)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            }
        }
    }

    // MARK: - Figures strip (En venta · [Pujas activas] · Seleccionadas)

    private var figuresStrip: some View {
        HStack(alignment: .top, spacing: DSSpacingSwiftUI.md) {
            // "En venta" is ALWAYS visible (BR6.1), independent of the toggle.
            figure("EN VENTA", money(onSaleTotal), color: DSColor.tertiary, alignment: .leading)
            // "Pujas activas (N)" only when N>0 (BR6.2).
            if activeBidsCount > 0 {
                figure(
                    "PUJAS ACTIVAS (\(activeBidsCount))",
                    "-\(money(activeBidsTotal))",
                    color: DSColor.moneyNegative,
                    alignment: .center
                )
            }
            figure(
                "SELECCIONADAS",
                money(selectedTotal),
                color: DSColor.primary,
                alignment: .trailing
            )
        }
    }

    private func figure(_ label: String, _ value: String, color: Color, alignment: HorizontalAlignment) -> some View {
        VStack(alignment: alignment, spacing: 2) {
            DSStatLabel(label)
            Text(value)
                .font(DSFont.body.weight(.bold))
                .foregroundStyle(color)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
        }
        .frame(maxWidth: .infinity, alignment: frameAlignment(alignment))
    }

    // MARK: - Toggle "Incorporar jugadores en venta" (FR3)

    private var includeToggle: some View {
        Toggle(isOn: Binding(
            get: { includeOnSale },
            set: { onToggleIncludeOnSale($0) }
        )) {
            Text("Incorporar jugadores en venta")
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurface)
        }
        .tint(DSColor.primary)
        .accessibilityHint("Con el ajuste activado, los jugadores en venta cuentan en En venta y se ocultan de la lista seleccionable")
    }

    // MARK: - Helpers

    private func money(_ amount: Int) -> String { MoneyFormatter.format(amount, signed: false) }

    private func frameAlignment(_ a: HorizontalAlignment) -> Alignment {
        switch a {
        case .leading: return .leading
        case .trailing: return .trailing
        default: return .center
        }
    }

    private var accessibilityLabel: String {
        var parts = [
            "Resumen económico.",
            "Saldo futuro \(MoneyFormatter.format(futureBalance, signed: true)).",
            "Saldo actual \(money(balance)).",
            "En venta \(money(onSaleTotal))."
        ]
        if activeBidsCount > 0 {
            parts.append("Pujas activas \(activeBidsCount), importe \(money(activeBidsTotal)).")
        }
        parts.append("Seleccionadas \(money(selectedTotal)).")
        return parts.joined(separator: " ")
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
