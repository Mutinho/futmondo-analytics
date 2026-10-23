import XCTest
@testable import FutmondoKit

final class BidAmountValidatorTests: XCTestCase {
    // Bounds reused across cases: market_price 500k, available_for_bids 2M.
    private let marketPrice = 500_000
    private let available = 2_000_000

    private func validate(_ amount: Int) -> BidAmountValidation {
        BidAmountValidator.validate(
            amount: amount,
            marketPrice: marketPrice,
            availableForBids: available
        )
    }

    // MARK: - 1. In-range amount is valid

    func testAmountInRangeIsValid() {
        XCTAssertEqual(validate(1_000_000), .valid)
    }

    // MARK: - 2. Boundary values are inclusive on both ends

    func testBoundariesAreInclusive() {
        XCTAssertEqual(validate(marketPrice), .valid, "== market_price is allowed")
        XCTAssertEqual(validate(available), .valid, "== available_for_bids is allowed")
    }

    // MARK: - 3. Zero and negative are nonPositive (precedence over tooLow)

    func testNonPositivePrecedence() {
        XCTAssertEqual(validate(0), .nonPositive)
        XCTAssertEqual(validate(-10), .nonPositive)
        // Even though -10 < market_price, nonPositive wins.
    }

    // MARK: - 4. Below market_price (but > 0) is tooLow with the minimum

    func testBelowMarketPriceIsTooLow() {
        XCTAssertEqual(validate(400_000), .tooLow(minimum: marketPrice))
    }

    // MARK: - 5. Above available_for_bids is tooHigh with the maximum

    func testAboveAvailableIsTooHigh() {
        XCTAssertEqual(validate(2_000_001), .tooHigh(maximum: available))
    }

    // MARK: - 6. BR-UI-2: the cap is available_for_bids, not max_bid

    func testCapIsAvailableNotMaxBid() {
        // available_for_bids = max_bid - active_bids_total. A value above
        // available but (hypothetically) below max_bid must still be tooHigh.
        let result = BidAmountValidator.validate(
            amount: 1_800_000,
            marketPrice: 100_000,
            availableForBids: 1_500_000 // < 1_800_000
        )
        XCTAssertEqual(result, .tooHigh(maximum: 1_500_000))
    }

    // MARK: - 7. Text parsing: valid integer string

    func testValidateTextParsesInteger() {
        let result = BidAmountValidator.validate(
            text: " 1000000 ",
            marketPrice: marketPrice,
            availableForBids: available
        )
        XCTAssertEqual(result, .valid)
    }

    // MARK: - 8. Text parsing: empty / non-numeric is nonPositive

    func testValidateTextNonNumericIsNonPositive() {
        for text in ["", "abc", "1,5", "1.0", " "] {
            let result = BidAmountValidator.validate(
                text: text,
                marketPrice: marketPrice,
                availableForBids: available
            )
            XCTAssertEqual(result, .nonPositive, "‘\(text)’ is not a plain integer")
        }
    }
}
