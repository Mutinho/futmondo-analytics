import Foundation

/// Deterministic, locale-independent money formatter (R1 / FR1.3).
///
/// Formatting rules (no `NumberFormatter`, no locale):
/// - `abs(amount) >= 1_000_000` → divide by 1_000_000, suffix `M`.
/// - `abs(amount) >= 1_000`     → divide by 1_000, suffix `K`.
/// - otherwise                  → the plain integer, no suffix.
/// - One decimal only when, after rounding to one decimal
///   (half-away-from-zero), the fractional tenth is non-zero
///   (`12,4M`); otherwise no decimal (`8M`, and `12,0M` → `12M`).
/// - Rounding is half-away-from-zero, computed with INTEGER arithmetic on the
///   magnitude so the result never depends on floating point or locale.
/// - Decimal separator is a fixed ASCII comma `,`; the negative sign is the
///   ASCII hyphen-minus `-` (U+002D); a leading `+` is emitted only when
///   `signed == true`.
public enum MoneyFormatter {
    /// Format `amount` (an integer number of currency units).
    ///
    /// - Parameters:
    ///   - amount: the signed amount.
    ///   - signed: when `true`, positive values are prefixed with `+`.
    public static func format(_ amount: Int, signed: Bool) -> String {
        let isNegative = amount < 0
        // Work on the magnitude. `magnitude` is the unsigned absolute value,
        // so `Int.min` does not overflow as it would with `abs`.
        let magnitude = UInt(amount.magnitude)

        let body: String
        if magnitude >= 1_000_000 {
            body = scaled(magnitude, divisor: 1_000_000, suffix: "M")
        } else if magnitude >= 1_000 {
            body = scaled(magnitude, divisor: 1_000, suffix: "K")
        } else {
            // Below 1_000: the plain integer, no suffix, no decimal.
            body = String(magnitude)
        }

        return applySign(body, isNegative: isNegative, signed: signed)
    }

    // MARK: - Scaling with integer half-away-from-zero rounding

    /// Divide `magnitude` by `divisor` and render it with at most one decimal,
    /// rounding that decimal half-away-from-zero using only integer math.
    private static func scaled(_ magnitude: UInt, divisor: UInt, suffix: String) -> String {
        // tenths = round(magnitude * 10 / divisor), half-away-from-zero.
        // Compute the quotient and remainder of (magnitude * 10) / divisor and
        // round up when twice the remainder reaches the divisor.
        let numerator = magnitude * 10
        var tenths = numerator / divisor
        let remainder = numerator % divisor
        if remainder * 2 >= divisor {
            tenths += 1
        }

        let whole = tenths / 10
        let decimal = tenths % 10

        if decimal == 0 {
            return "\(whole)\(suffix)"
        }
        return "\(whole),\(decimal)\(suffix)"
    }

    // MARK: - Sign

    private static func applySign(_ body: String, isNegative: Bool, signed: Bool) -> String {
        if isNegative {
            return "-\(body)"
        }
        if signed {
            return "+\(body)"
        }
        return body
    }
}
