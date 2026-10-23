import XCTest
@testable import FutmondoKit

/// Deterministic, locale-independent table for `MoneyFormatter`.
final class MoneyFormatterTests: XCTestCase {

    // MARK: - 1. Unsigned table (happy path + boundaries)

    func testUnsignedTable() {
        let cases: [(Int, String)] = [
            (12_400_000, "12,4M"),   // one decimal when non-zero tenth
            (8_000_000, "8M"),       // no decimal when zero tenth
            (12_000_000, "12M"),     // exact integer million
            (11_990_000, "12M"),     // rounds to 12,0 → emitted as 12M
            (5_500, "5,5K"),         // thousands with decimal
            (950, "950")             // below 1_000: plain integer, no suffix
        ]
        for (amount, expected) in cases {
            XCTAssertEqual(
                MoneyFormatter.format(amount, signed: false),
                expected,
                "format(\(amount), signed: false)"
            )
        }
    }

    // MARK: - 2. Negative, unsigned (only `-`, no `+`)

    func testNegativeUnsigned() {
        XCTAssertEqual(MoneyFormatter.format(-1_200_000, signed: false), "-1,2M")
        // Half-away-from-zero: 1,25M rounds AWAY from zero to 1,3M.
        XCTAssertEqual(MoneyFormatter.format(-1_250_000, signed: false), "-1,3M")
    }

    // MARK: - 3. Half-away-from-zero is symmetric

    func testHalfAwayFromZeroSymmetry() {
        XCTAssertEqual(MoneyFormatter.format(1_250_000, signed: false), "1,3M")
        XCTAssertEqual(MoneyFormatter.format(-1_250_000, signed: false), "-1,3M")
        // 5_450 → 5,45K → rounds to 5,5K (away from zero at the half).
        XCTAssertEqual(MoneyFormatter.format(5_450, signed: false), "5,5K")
    }

    // MARK: - 4. Signed mode

    func testSignedMode() {
        XCTAssertEqual(MoneyFormatter.format(3_100_000, signed: true), "+3,1M")
        XCTAssertEqual(MoneyFormatter.format(-500_000, signed: true), "-500K")
        XCTAssertEqual(MoneyFormatter.format(0, signed: true), "+0")
    }

    // MARK: - 5. Zero and small values

    func testZeroAndSmall() {
        XCTAssertEqual(MoneyFormatter.format(0, signed: false), "0")
        XCTAssertEqual(MoneyFormatter.format(-0, signed: false), "0")
        XCTAssertEqual(MoneyFormatter.format(-999, signed: false), "-999")
        XCTAssertEqual(MoneyFormatter.format(999, signed: false), "999")
    }

    // MARK: - 6. Glyphs are ASCII and locale-independent

    func testGlyphsAreASCIIAndLocaleIndependent() {
        let formatted = MoneyFormatter.format(-1_200_000, signed: false)
        // Decimal separator is a fixed ASCII comma, not a locale separator.
        XCTAssertTrue(formatted.contains(","))
        XCTAssertFalse(formatted.contains("."))
        // The negative sign is ASCII hyphen-minus (U+002D), not U+2212.
        XCTAssertTrue(formatted.unicodeScalars.contains(Unicode.Scalar(0x2D)))
        XCTAssertFalse(formatted.unicodeScalars.contains(Unicode.Scalar(0x2212)!))
    }

    // MARK: - 7. Thousands boundary

    func testThousandsBoundary() {
        XCTAssertEqual(MoneyFormatter.format(1_000, signed: false), "1K")
        XCTAssertEqual(MoneyFormatter.format(999_999, signed: false), "1000K")
        XCTAssertEqual(MoneyFormatter.format(1_000_000, signed: false), "1M")
    }
}
