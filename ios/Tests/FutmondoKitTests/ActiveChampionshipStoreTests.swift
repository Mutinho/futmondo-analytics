import XCTest
@testable import FutmondoKit

final class ActiveChampionshipStoreTests: XCTestCase {
    private var suiteName: String!
    private var defaults: UserDefaults!

    override func setUp() {
        super.setUp()
        // A dedicated, isolated suite per test instance, cleared before use.
        suiteName = "test.futmondo.active.\(UUID().uuidString)"
        defaults = UserDefaults(suiteName: suiteName)
        defaults.removePersistentDomain(forName: suiteName)
    }

    override func tearDown() {
        defaults.removePersistentDomain(forName: suiteName)
        defaults = nil
        suiteName = nil
        super.tearDown()
    }

    // MARK: - 1. No value → activeId is nil

    func testActiveIdIsNilWhenEmpty() {
        let store = UserDefaultsActiveChampionshipStore(defaults: defaults)
        XCTAssertNil(store.activeId)
    }

    // MARK: - 2. setActive persists and is re-read

    func testSetActivePersistsAndReads() {
        let store = UserDefaultsActiveChampionshipStore(defaults: defaults)
        store.setActive("champ-42")
        XCTAssertEqual(store.activeId, "champ-42")
        // Persisted under the exact shared key.
        XCTAssertEqual(
            defaults.string(forKey: UserDefaultsActiveChampionshipStore.key),
            "champ-42"
        )
    }

    // MARK: - 3. A new store instance reads the persisted value

    func testPersistedValueSurvivesNewStoreInstance() {
        UserDefaultsActiveChampionshipStore(defaults: defaults).setActive("champ-persist")
        let reopened = UserDefaultsActiveChampionshipStore(defaults: defaults)
        XCTAssertEqual(reopened.activeId, "champ-persist")
    }

    // MARK: - 4. setActive overwrites the previous value

    func testSetActiveOverwrites() {
        let store = UserDefaultsActiveChampionshipStore(defaults: defaults)
        store.setActive("first")
        store.setActive("second")
        XCTAssertEqual(store.activeId, "second")
    }

    // MARK: - 5. Only the id string is stored (no object graph)

    func testStoresOnlyAStringUnderTheKey() {
        let store = UserDefaultsActiveChampionshipStore(defaults: defaults)
        store.setActive("champ-x")
        let raw = defaults.object(forKey: UserDefaultsActiveChampionshipStore.key)
        XCTAssertTrue(raw is String, "the store must persist a plain String id")
    }
}

final class ActiveChampionshipResolverTests: XCTestCase {
    private func champ(_ id: String) -> Championship {
        Championship(
            championshipId: id,
            name: "Name \(id)",
            initialBudget: 0,
            hasClauses: false,
            excludedTeams: []
        )
    }

    // MARK: - 1. activeId in list → that championship

    func testActiveIdInListReturnsThatChampionship() {
        let list = [champ("a"), champ("b"), champ("c")]
        let resolved = ActiveChampionshipResolver.resolve(activeId: "b", in: list)
        XCTAssertEqual(resolved?.championshipId, "b")
    }

    // MARK: - 2. activeId nil → first

    func testNilActiveIdReturnsFirst() {
        let list = [champ("a"), champ("b")]
        let resolved = ActiveChampionshipResolver.resolve(activeId: nil, in: list)
        XCTAssertEqual(resolved?.championshipId, "a")
    }

    // MARK: - 3. activeId not in list → first

    func testUnknownActiveIdReturnsFirst() {
        let list = [champ("a"), champ("b")]
        let resolved = ActiveChampionshipResolver.resolve(activeId: "zzz", in: list)
        XCTAssertEqual(resolved?.championshipId, "a")
    }

    // MARK: - 4. empty list → nil

    func testEmptyListReturnsNil() {
        let resolved = ActiveChampionshipResolver.resolve(activeId: "a", in: [])
        XCTAssertNil(resolved)
    }

    // MARK: - 5. empty list with nil activeId → nil

    func testEmptyListNilActiveIdReturnsNil() {
        XCTAssertNil(ActiveChampionshipResolver.resolve(activeId: nil, in: []))
    }
}
