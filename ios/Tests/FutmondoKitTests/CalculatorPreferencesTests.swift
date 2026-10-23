import XCTest
@testable import FutmondoKit

final class CalculatorPreferencesTests: XCTestCase {

    // MARK: - 1. default includeOnSale is ON when nothing stored (BR5.1)

    func testIncludeOnSaleDefaultsOn() {
        let prefs = CalculatorPreferences(store: InMemoryKeyValueStore())
        XCTAssertTrue(prefs.includeOnSale, "absent value resolves to ON")
    }

    // MARK: - 2. only the literal 'false' resolves to OFF (BR5.1)

    func testOnlyFalseLiteralIsOff() {
        let falseStore = InMemoryKeyValueStore(initial: [CalculatorPreferences.Key.includeOnSale: "false"])
        XCTAssertFalse(CalculatorPreferences(store: falseStore).includeOnSale)

        // Any other stored value (incl. legacy/garbage) resolves to ON.
        let trueStore = InMemoryKeyValueStore(initial: [CalculatorPreferences.Key.includeOnSale: "true"])
        XCTAssertTrue(CalculatorPreferences(store: trueStore).includeOnSale)

        let oddStore = InMemoryKeyValueStore(initial: [CalculatorPreferences.Key.includeOnSale: "0"])
        XCTAssertTrue(CalculatorPreferences(store: oddStore).includeOnSale, "non-'false' resolves to ON")
    }

    // MARK: - 3. includeOnSale round-trips through the store

    func testIncludeOnSaleRoundTrip() {
        let store = InMemoryKeyValueStore()
        let prefs = CalculatorPreferences(store: store)

        prefs.includeOnSale = false
        XCTAssertFalse(prefs.includeOnSale)
        XCTAssertEqual(store.string(forKey: CalculatorPreferences.Key.includeOnSale), "false")

        prefs.includeOnSale = true
        XCTAssertTrue(prefs.includeOnSale)
        XCTAssertEqual(store.string(forKey: CalculatorPreferences.Key.includeOnSale), "true")
    }

    // MARK: - 4. sortField defaults to projectedValue and round-trips (FR5.3)

    func testSortFieldDefaultAndRoundTrip() {
        let store = InMemoryKeyValueStore()
        let prefs = CalculatorPreferences(store: store)
        XCTAssertEqual(prefs.sortField, .projectedValue, "default")

        prefs.sortField = .change
        XCTAssertEqual(prefs.sortField, .change)
        XCTAssertEqual(store.string(forKey: CalculatorPreferences.Key.sortField), "change")

        prefs.sortField = .profit
        XCTAssertEqual(prefs.sortField, .profit)
    }

    // MARK: - 5. an unrecognized stored sort field falls back to the default

    func testUnknownSortFieldFallsBack() {
        let store = InMemoryKeyValueStore(initial: [CalculatorPreferences.Key.sortField: "bogus"])
        XCTAssertEqual(CalculatorPreferences(store: store).sortField, .projectedValue)
    }
}
