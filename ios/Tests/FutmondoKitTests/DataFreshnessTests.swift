import XCTest
@testable import FutmondoKit

/// Tests for `DataFreshness`: the in-memory TTL + per-championship policy that
/// stops tab switches from refetching the API.
final class DataFreshnessTests: XCTestCase {

    private let t0 = Date(timeIntervalSince1970: 1_000_000)

    func testNeverLoadedReloads() {
        let f = DataFreshness(ttl: 180)
        XCTAssertTrue(f.shouldReload(activeId: "champ-1", now: t0))
    }

    func testNilOrEmptyActiveIdAlwaysReloads() {
        var f = DataFreshness(ttl: 180)
        f.markLoaded(championshipId: "champ-1", now: t0)
        XCTAssertTrue(f.shouldReload(activeId: nil, now: t0))
        XCTAssertTrue(f.shouldReload(activeId: "", now: t0))
    }

    func testSameChampionshipWithinTTLDoesNotReload() {
        var f = DataFreshness(ttl: 180)
        f.markLoaded(championshipId: "champ-1", now: t0)
        // 2 minutes later, same championship → still fresh.
        XCTAssertFalse(f.shouldReload(activeId: "champ-1", now: t0.addingTimeInterval(120)))
    }

    func testChampionshipChangeReloadsEvenWithinTTL() {
        var f = DataFreshness(ttl: 180)
        f.markLoaded(championshipId: "champ-1", now: t0)
        XCTAssertTrue(f.shouldReload(activeId: "champ-2", now: t0.addingTimeInterval(10)))
    }

    func testTTLExpiryReloads() {
        var f = DataFreshness(ttl: 180)
        f.markLoaded(championshipId: "champ-1", now: t0)
        // Exactly at the TTL boundary and beyond → stale.
        XCTAssertTrue(f.shouldReload(activeId: "champ-1", now: t0.addingTimeInterval(180)))
        XCTAssertTrue(f.shouldReload(activeId: "champ-1", now: t0.addingTimeInterval(300)))
    }

    func testInvalidateForcesReload() {
        var f = DataFreshness(ttl: 180)
        f.markLoaded(championshipId: "champ-1", now: t0)
        XCTAssertFalse(f.shouldReload(activeId: "champ-1", now: t0.addingTimeInterval(1)))
        f.invalidate()
        XCTAssertTrue(f.shouldReload(activeId: "champ-1", now: t0.addingTimeInterval(1)))
    }

    func testReloadAfterMarkingUsesLatestLoadTime() {
        var f = DataFreshness(ttl: 100)
        f.markLoaded(championshipId: "champ-1", now: t0)
        // Re-mark later resets the clock.
        f.markLoaded(championshipId: "champ-1", now: t0.addingTimeInterval(90))
        XCTAssertFalse(f.shouldReload(activeId: "champ-1", now: t0.addingTimeInterval(150)))
        XCTAssertTrue(f.shouldReload(activeId: "champ-1", now: t0.addingTimeInterval(190)))
    }
}
