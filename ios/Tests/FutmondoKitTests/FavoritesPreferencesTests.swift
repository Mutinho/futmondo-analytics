import XCTest
@testable import FutmondoKit

final class FavoritesPreferencesTests: XCTestCase {

    // MARK: - 1. sortField defaults to value when nothing stored (BR4.1)

    func testSortFieldDefaultsToValue() {
        let prefs = FavoritesPreferences(store: InMemoryKeyValueStore())
        XCTAssertEqual(prefs.sortField, .value, "absent value resolves to the default")
    }

    // MARK: - 2. sortField round-trips through the store

    func testSortFieldRoundTrip() {
        let store = InMemoryKeyValueStore()
        let prefs = FavoritesPreferences(store: store)

        prefs.sortField = .sofascoreRating
        XCTAssertEqual(prefs.sortField, .sofascoreRating)
        XCTAssertEqual(store.string(forKey: FavoritesPreferences.Key.sortField), "sofascoreRating")

        prefs.sortField = .points
        XCTAssertEqual(prefs.sortField, .points)
        XCTAssertEqual(store.string(forKey: FavoritesPreferences.Key.sortField), "points")
    }

    // MARK: - 3. an unrecognized stored sort field falls back to the default

    func testUnknownSortFieldFallsBack() {
        let store = InMemoryKeyValueStore(initial: [FavoritesPreferences.Key.sortField: "bogus"])
        XCTAssertEqual(FavoritesPreferences(store: store).sortField, .value)
    }

    // MARK: - 4. a stored value survives across separate instances (persistence)

    func testSortFieldPersistsAcrossInstances() {
        let store = InMemoryKeyValueStore()
        FavoritesPreferences(store: store).sortField = .change
        // A fresh instance over the SAME store reads the persisted value.
        XCTAssertEqual(FavoritesPreferences(store: store).sortField, .change)
    }
}
