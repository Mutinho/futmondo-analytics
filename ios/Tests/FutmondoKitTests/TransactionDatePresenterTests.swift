import XCTest
@testable import FutmondoKit

final class TransactionDatePresenterTests: XCTestCase {
    // MARK: - 1. ISO yyyy-MM-dd maps to dd/MM/yyyy

    func testPlainIsoDateMapsToDayMonthYear() {
        XCTAssertEqual(TransactionDatePresenter.display("2026-01-15"), "15/01/2026")
    }

    // MARK: - 2. ISO with a time suffix keeps only the date part

    func testIsoWithTimeSuffixDropsTime() {
        XCTAssertEqual(
            TransactionDatePresenter.display("2026-02-01T18:30:00Z"),
            "01/02/2026"
        )
        XCTAssertEqual(
            TransactionDatePresenter.display("2026-12-31 23:59:59"),
            "31/12/2026"
        )
    }

    // MARK: - 3. Single-digit month/day are zero-padded

    func testSingleDigitComponentsArePadded() {
        XCTAssertEqual(TransactionDatePresenter.display("2026-3-7"), "07/03/2026")
    }

    // MARK: - 4. A non-ISO string is returned unchanged (never breaks a row)

    func testUnparseableStringReturnedVerbatim() {
        XCTAssertEqual(TransactionDatePresenter.display("ayer"), "ayer")
        XCTAssertEqual(TransactionDatePresenter.display(""), "")
        XCTAssertEqual(TransactionDatePresenter.display("2026/01/15"), "2026/01/15")
        XCTAssertEqual(TransactionDatePresenter.display("2026-01"), "2026-01")
    }

    // MARK: - 5. Non-numeric components fall through unchanged

    func testNonNumericComponentsReturnedVerbatim() {
        XCTAssertEqual(TransactionDatePresenter.display("abcd-ef-gh"), "abcd-ef-gh")
    }
}
