import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI

/// Bid composition sheet (V4 / W4 / FR6.2), redesigned as a modern, native,
/// high-impact control instead of a plain text field:
///
/// - A HERO amount that animates on change, money-coloured by validity.
/// - A native `Slider` bounded to `[market_price, available_for_bids]` for
///   coarse selection, plus a `Stepper` (±25k) for fine control — both drive
///   the SAME integer the pure `BidAmountValidator` checks (BR-UI-1/2).
/// - Tappable reference chips (Mínimo / Sugerida / Máximo) that snap the amount.
/// - A live "usa X % de tu disponible" gauge so the manager feels the commitment.
/// - Light haptics on step/snap and a success tap on confirm (UIKit only).
///
/// The backend remains authoritative; this is UX. "Pujar" is disabled while the
/// amount is invalid (empty/≤0, below market price, or above available).
@available(iOS 17.0, macOS 14.0, *)
public struct BidSheet: View {
    private let player: MarketPlayer
    private let userInfo: MarketUserInfo
    private let onConfirm: (Int) -> Void

    @State private var amount: Int
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(
        player: MarketPlayer,
        userInfo: MarketUserInfo,
        onConfirm: @escaping (Int) -> Void
    ) {
        self.player = player
        self.userInfo = userInfo
        self.onConfirm = onConfirm
        _amount = State(initialValue: player.suggestedBid)
    }

    // Slider bounds: the effective cap is available_for_bids (BR-UI-2). Guard a
    // degenerate range (cap < market price) so the Slider never crashes.
    private var minBound: Int { player.marketPrice }
    private var maxBound: Int { max(player.marketPrice, userInfo.availableForBids) }
    private var sliderRange: ClosedRange<Double> { Double(minBound)...Double(max(minBound + 1, maxBound)) }

    private var validation: BidAmountValidation {
        BidAmountValidator.validate(
            amount: amount,
            marketPrice: player.marketPrice,
            availableForBids: userInfo.availableForBids
        )
    }
    private var isValid: Bool { validation == .valid }

    /// Fraction of the available budget this bid commits (0...1), for the gauge.
    private var availableFraction: Double {
        guard userInfo.availableForBids > 0 else { return amount > 0 ? 1 : 0 }
        return min(1, max(0, Double(amount) / Double(userInfo.availableForBids)))
    }

    private var errorMessage: String? {
        switch validation {
        case .valid: return nil
        case .nonPositive: return "El importe debe ser mayor que 0"
        case .tooLow(let minimum): return "Mínimo: \(money(minimum))"
        case .tooHigh(let maximum): return "Máximo disponible: \(money(maximum))"
        }
    }

    public var body: some View {
        NavigationStack {
            VStack(spacing: DSSpacingSwiftUI.lg) {
                amountField
                sliderBlock
                referenceChips
                if let errorMessage {
                    inlineError(errorMessage)
                }
                Spacer(minLength: 0)
                confirmBar
            }
            .padding(DSSpacingSwiftUI.lg)
            .frame(maxWidth: .infinity)
            .background(DSColor.surface)
            .navigationTitle(player.name)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancelar") { dismiss() }
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
        .accessibilityIdentifier("bid-sheet")
    }

    // MARK: - Editable amount field (precise) + commitment gauge

    /// Precise, editable amount. The big rounded number IS a `TextField` bound
    /// to the integer, so the manager can type an exact figure OR drive it from
    /// the slider/chips — both stay in sync. Money-coloured by validity; the
    /// native numeric keyboard is used on device. A trailing € keeps context.
    private var amountField: some View {
        VStack(spacing: DSSpacingSwiftUI.sm) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                TextField("0", value: $amount, format: .number)
                    .font(.system(size: 44, weight: .heavy, design: .rounded))
                    .foregroundStyle(isValid ? DSColor.onSurface : DSColor.moneyNegative)
                    .multilineTextAlignment(.center)
                    .fixedSize()
                    .modifier(NumericKeyboardIfAvailable())
                    .onChange(of: amount) { _, newValue in
                        // Keep typed input within bounds without fighting the
                        // user mid-edit: clamp only the high end live; the low
                        // end is validated (so "below minimum" can be shown).
                        if newValue > maxBound { amount = maxBound }
                        if newValue < 0 { amount = 0 }
                    }
                    .accessibilityLabel("Importe de puja en euros")
                Text("€")
                    .font(.system(size: 28, weight: .bold, design: .rounded))
                    .foregroundStyle(DSColor.onSurfaceVariant)
            }

            // Native Gauge (iOS 16+) showing how much of the available this bid
            // uses; falls back to a slim capacity bar on older runtimes.
            commitmentGauge
        }
    }

    @ViewBuilder
    private var commitmentGauge: some View {
        if #available(iOS 16.0, *) {
            Gauge(value: availableFraction) {
                EmptyView()
            } currentValueLabel: {
                Text("\(Int((availableFraction * 100).rounded()))%")
            }
            .gaugeStyle(.accessoryLinearCapacity)
            .tint(isValid ? DSColor.moneyPositive : DSColor.moneyNegative)
            .animation(reduceMotion ? nil : .snappy, value: availableFraction)
            .accessibilityLabel("Usa el \(Int((availableFraction * 100).rounded())) por ciento de tu disponible")
        } else {
            Text("Usa \(Int((availableFraction * 100).rounded()))% de tu disponible")
                .font(.caption)
                .foregroundStyle(DSColor.onSurfaceVariant)
        }
    }

    // MARK: - Slider + Stepper (coarse + fine, native)

    private var sliderBlock: some View {
        VStack(spacing: DSSpacingSwiftUI.sm) {
            Slider(
                value: Binding(
                    get: { Double(amount) },
                    set: { newValue in setAmount(Int(newValue.rounded()), haptic: .selection) }
                ),
                in: sliderRange
            ) {
                Text("Importe")
            } minimumValueLabel: {
                Text(moneyShort(minBound)).font(.caption2).foregroundStyle(DSColor.onSurfaceVariant)
            } maximumValueLabel: {
                Text(moneyShort(maxBound)).font(.caption2).foregroundStyle(DSColor.onSurfaceVariant)
            }
            .tint(DSColor.primary)
            .accessibilityLabel("Ajustar importe entre \(money(minBound)) y \(money(maxBound))")

            HStack {
                Text("Ajuste fino")
                    .font(.caption)
                    .foregroundStyle(DSColor.onSurfaceVariant)
                Spacer()
                Stepper(
                    "",
                    onIncrement: { setAmount(amount + stepSize, haptic: .light) },
                    onDecrement: { setAmount(amount - stepSize, haptic: .light) }
                )
                .labelsHidden()
                .accessibilityLabel("Ajustar importe en pasos de \(money(stepSize))")
            }
        }
    }

    /// Fine-step size: ~1/40 of the range rounded to 10k, clamped to
    /// [25k, 100k], so the stepper stays useful on both small and big budgets.
    private var stepSize: Int {
        let span = maxBound - minBound
        guard span > 0 else { return 25_000 }
        let rounded = (span / 40) / 10_000 * 10_000
        return min(100_000, max(25_000, rounded))
    }

    // MARK: - Reference chips (tap to snap)

    private var referenceChips: some View {
        HStack(spacing: DSSpacingSwiftUI.sm) {
            snapChip("Mínimo", player.marketPrice)
            snapChip("Sugerida", player.suggestedBid, accent: true)
            snapChip("Máximo", userInfo.availableForBids)
        }
    }

    private func snapChip(_ label: String, _ value: Int, accent: Bool = false) -> some View {
        let selected = amount == value
        return Button {
            setAmount(value, haptic: .selection)
        } label: {
            VStack(spacing: 2) {
                Text(label.uppercased())
                    .font(.caption2.weight(.heavy))
                    .foregroundStyle(DSColor.onSurfaceVariant)
                Text(moneyShort(value))
                    .font(DSFont.body.weight(.semibold))
                    .foregroundStyle(accent ? DSColor.primary : DSColor.onSurface)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, DSSpacingSwiftUI.sm)
            .background((selected ? DSColor.primary : DSColor.onSurfaceVariant).opacity(selected ? 0.18 : 0.08))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(DSColor.primary.opacity(selected ? 0.6 : 0.0), lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(label) \(money(value))")
        .accessibilityAddTraits(selected ? [.isSelected] : [])
    }

    // MARK: - Inline error + confirm bar

    private func inlineError(_ message: String) -> some View {
        HStack(spacing: DSSpacingSwiftUI.xs) {
            Image(systemName: "exclamationmark.triangle.fill").accessibilityHidden(true)
            Text(message).font(.caption)
        }
        .foregroundStyle(DSColor.moneyNegative)
        .frame(maxWidth: .infinity, alignment: .leading)
        .transition(.opacity.combined(with: .move(edge: .top)))
    }

    private var confirmBar: some View {
        PrimaryButton(title: "Pujar \(moneyShort(amount))", isEnabled: isValid) {
            successHaptic()
            onConfirm(amount)
            dismiss()
        }
    }

    // MARK: - Amount mutation + haptics

    private enum Hap { case selection, light }

    private func setAmount(_ newValue: Int, haptic: Hap) {
        let clamped = min(maxBound, max(minBound, newValue))
        guard clamped != amount else { return }
        withAnimation(reduceMotion ? nil : .snappy) { amount = clamped }
        fireHaptic(haptic)
    }

    private func fireHaptic(_ h: Hap) {
        #if canImport(UIKit)
        switch h {
        case .selection:
            UISelectionFeedbackGenerator().selectionChanged()
        case .light:
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
        }
        #endif
    }

    private func successHaptic() {
        #if canImport(UIKit)
        UINotificationFeedbackGenerator().notificationOccurred(.success)
        #endif
    }

    // MARK: - Formatting

    private func money(_ amount: Int) -> String { MoneyFormatter.format(amount, signed: false) }

    /// Compact money for chips/labels: "1,2 M" / "850 k" style, locale-light.
    private func moneyShort(_ amount: Int) -> String {
        let a = abs(amount)
        if a >= 1_000_000 {
            let m = Double(amount) / 1_000_000
            return String(format: "%.1f M€", m)
        }
        if a >= 1_000 {
            return "\(amount / 1_000) k€"
        }
        return money(amount)
    }
}

/// Applies the numeric keyboard on iOS (UIKit); a no-op on macOS/Linux dev
/// builds. Factored into a modifier so the `#if canImport(UIKit)` guard stays
/// off the field body.
@available(iOS 15.0, macOS 12.0, *)
private struct NumericKeyboardIfAvailable: ViewModifier {
    func body(content: Content) -> some View {
        #if canImport(UIKit)
        content.keyboardType(.numberPad)
        #else
        content
        #endif
    }
}

#endif // canImport(SwiftUI) && canImport(Observation)
