import Foundation

/// Pure client-side validation of a bid amount (FR6.2 / W4 / BR-UI-1 / C7).
///
/// The bid must be `> 0`, at least `market_price`, and at most
/// `available_for_bids` (the effective cap, `max_bid - active_bids_total`,
/// BR-UI-2). This is UX only; the backend revalidates and remains authoritative
/// (`price > 0`, `price <= PRICE_SANITY_CAP`).
///
/// `.nonPositive` takes precedence over `.tooLow`: an empty or `<= 0` amount is
/// reported as "mayor que 0" rather than "menor que el mínimo".
public enum BidAmountValidation: Sendable, Equatable {
    case valid
    case nonPositive
    case tooLow(minimum: Int)
    case tooHigh(maximum: Int)
}

/// Stateless validator producing a ``BidAmountValidation`` from an amount and
/// the player's price bounds.
public enum BidAmountValidator {
    /// Validate `amount` against `[marketPrice, availableForBids]` and `> 0`.
    ///
    /// - `amount <= 0` → `.nonPositive` (highest precedence).
    /// - `amount < marketPrice` → `.tooLow(minimum: marketPrice)`.
    /// - `amount > availableForBids` → `.tooHigh(maximum: availableForBids)`.
    /// - otherwise → `.valid`.
    public static func validate(
        amount: Int,
        marketPrice: Int,
        availableForBids: Int
    ) -> BidAmountValidation {
        guard amount > 0 else {
            return .nonPositive
        }
        if amount < marketPrice {
            return .tooLow(minimum: marketPrice)
        }
        if amount > availableForBids {
            return .tooHigh(maximum: availableForBids)
        }
        return .valid
    }

    /// Convenience parse-and-validate for a raw text field. A non-integer or
    /// empty string is `.nonPositive` (nothing to bid). The string is trimmed
    /// and must be a plain base-10 integer (the field uses a numeric keyboard).
    public static func validate(
        text: String,
        marketPrice: Int,
        availableForBids: Int
    ) -> BidAmountValidation {
        let trimmed = text.trimmingCharacters(in: .whitespaces)
        guard let amount = Int(trimmed) else {
            return .nonPositive
        }
        return validate(
            amount: amount,
            marketPrice: marketPrice,
            availableForBids: availableForBids
        )
    }
}
