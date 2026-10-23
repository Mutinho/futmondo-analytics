import XCTest
@testable import FutmondoKit

/// Tests for the pure persistence decision (R5 / FR3.3). This is the one piece
/// of new U2 logic cleanly extractable from the SwiftUI-bound `BudgetViewModel`
/// — the views and the view model itself are device-validated (coverage of UI
/// is unreliable on Linux/WSL, durable rule).
final class ActiveChampionshipPersistenceTests: XCTestCase {

    func testPersistsWhenResolvedDiffersFromStored() {
        XCTAssertTrue(
            ActiveChampionshipPersistence.shouldPersist(resolvedId: "c2", storedId: "c1")
        )
    }

    func testPersistsWhenNothingStoredYet() {
        XCTAssertTrue(
            ActiveChampionshipPersistence.shouldPersist(resolvedId: "c1", storedId: nil)
        )
    }

    func testDoesNotPersistWhenResolvedEqualsStored() {
        XCTAssertFalse(
            ActiveChampionshipPersistence.shouldPersist(resolvedId: "c1", storedId: "c1")
        )
    }

    func testDoesNotPersistWhenNothingResolved() {
        // Empty championship list → nil resolved id → never writes, so a
        // failure/empty state cannot wipe the stored active id (FR4.2).
        XCTAssertFalse(
            ActiveChampionshipPersistence.shouldPersist(resolvedId: nil, storedId: "c1")
        )
    }

    func testDoesNotPersistWhenBothNil() {
        XCTAssertFalse(
            ActiveChampionshipPersistence.shouldPersist(resolvedId: nil, storedId: nil)
        )
    }
}
