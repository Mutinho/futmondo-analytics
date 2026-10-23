import XCTest
@testable import FutmondoKit

final class RosterPlayerTests: XCTestCase {
    private let decoder = JSONDecoder()

    // MARK: - 1. RosterPlayer maps snake_case incl. buy_price/profit/change

    func testRosterPlayerDecodesSnakeCase() throws {
        let json = #"""
        {
          "player_id": "p-1", "name": "Vinicius", "slug": "vinicius-jr",
          "position": "Delantero", "position2": "Medio",
          "team": "Real Madrid", "team_logo": "rm.png",
          "value": 80000000, "buy_price": 60000000, "profit": 20000000,
          "change": 150000, "points": 142, "average": 7.4, "matches": 20,
          "sofascore_rating": 7.8, "sofascore_url": "https://sofascore/x",
          "starter_pct": 95, "status": "ok",
          "ignored_extra": true
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(RosterPlayer.self, from: json)
        XCTAssertEqual(player.playerId, "p-1")
        XCTAssertEqual(player.id, "p-1")
        XCTAssertEqual(player.name, "Vinicius")
        XCTAssertEqual(player.slug, "vinicius-jr")
        XCTAssertEqual(player.value, 80_000_000)
        XCTAssertEqual(player.buyPrice, 60_000_000)
        XCTAssertEqual(player.profit, 20_000_000)
        XCTAssertEqual(player.change, 150_000)
        XCTAssertEqual(player.teamLogo, "rm.png")
        XCTAssertEqual(player.sofascoreRating, 7.8)
        XCTAssertEqual(player.starterPct, 95)
        XCTAssertEqual(player.status, "ok")
    }

    // MARK: - 2. Nullable analytics decode to nil (null & absent)

    func testRosterPlayerNullableFieldsDecodeToNil() throws {
        let json = #"""
        {
          "player_id": "p-2", "name": "N", "slug": "s", "team": "T",
          "value": 1000000,
          "change": null, "profit": null, "sofascore_rating": null,
          "starter_pct": null, "points": null, "average": null
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(RosterPlayer.self, from: json)
        XCTAssertNil(player.change)
        XCTAssertNil(player.profit)
        XCTAssertNil(player.buyPrice, "absent optional decodes to nil")
        XCTAssertNil(player.sofascoreRating)
        XCTAssertNil(player.starterPct)
    }

    // MARK: - 3. Missing required field fails decoding (strict)

    func testRosterPlayerMissingValueThrows() {
        let json = #"""
        { "player_id": "p-1", "name": "N", "slug": "s", "team": "T" }
        """#.data(using: .utf8)!  // missing value
        XCTAssertThrowsError(try decoder.decode(RosterPlayer.self, from: json))
    }

    // MARK: - 4. RosterResponse tolerates both root-array and wrapped shapes

    func testRosterResponseRootArray() throws {
        let json = #"""
        [
          { "player_id": "a", "name": "A", "slug": "a", "team": "T", "value": 1 },
          { "player_id": "b", "name": "B", "slug": "b", "team": "T", "value": 2 }
        ]
        """#.data(using: .utf8)!
        let response = try decoder.decode(RosterResponse.self, from: json)
        XCTAssertEqual(response.players.map(\.playerId), ["a", "b"])
    }

    func testRosterResponseWrapped() throws {
        let json = #"""
        { "players": [ { "player_id": "a", "name": "A", "slug": "a", "team": "T", "value": 1 } ] }
        """#.data(using: .utf8)!
        let response = try decoder.decode(RosterResponse.self, from: json)
        XCTAssertEqual(response.players.count, 1)
    }

    // MARK: - 5. OnSalePlayer decode + OnSaleResponse shapes

    func testOnSalePlayerDecodes() throws {
        let json = #"""
        { "player_id": "x", "name": "X", "slug": "x", "team": "T", "value": 500000 }
        """#.data(using: .utf8)!
        let p = try decoder.decode(OnSalePlayer.self, from: json)
        XCTAssertEqual(p.playerId, "x")
        XCTAssertEqual(p.value, 500_000)

        let sparse = #"""
        { "player_id": "y", "name": "Y", "slug": "y", "value": 100 }
        """#.data(using: .utf8)!
        let sparseP = try decoder.decode(OnSalePlayer.self, from: sparse)
        XCTAssertNil(sparseP.team, "team is tolerated as optional (A2)")
    }

    // MARK: - 6. R-02 regression: active_bids_count ABSENT decodes to 0

    func testMarketUserInfoActiveBidsCountAbsentDefaultsToZero() throws {
        // The EXISTING market/today payload (no active_bids_count) must still
        // decode after the field was added, defaulting the count to 0.
        let json = #"""
        {
          "balance": 10000000, "team_value": 50000000, "max_bid": 20000000,
          "active_bids_total": 3000000, "available_for_bids": 17000000
        }
        """#.data(using: .utf8)!
        let info = try decoder.decode(MarketUserInfo.self, from: json)
        XCTAssertEqual(info.activeBidsCount, 0, "absent active_bids_count → 0 (no decode break)")
        XCTAssertEqual(info.balance, 10_000_000)
    }

    // MARK: - 7. R-02: active_bids_count PRESENT decodes its value

    func testMarketUserInfoActiveBidsCountPresent() throws {
        let json = #"""
        {
          "balance": 10000000, "team_value": 0, "max_bid": 0,
          "active_bids_total": 3000000, "available_for_bids": 7000000,
          "active_bids_count": 4
        }
        """#.data(using: .utf8)!
        let info = try decoder.decode(MarketUserInfo.self, from: json)
        XCTAssertEqual(info.activeBidsCount, 4)
    }

    // MARK: - 8. Memberwise init still works without active_bids_count (no caller break)

    func testMarketUserInfoMemberwiseInitBackwardCompatible() {
        // The existing Mercado callers never pass active_bids_count; the
        // defaulted LAST parameter keeps them compiling and defaults to 0.
        let info = MarketUserInfo(
            balance: 1, teamValue: 2, maxBid: 3,
            activeBidsTotal: 4, availableForBids: 5
        )
        XCTAssertEqual(info.activeBidsCount, 0)
    }

    // MARK: - 9. SellOutcome classification (BR8.2)

    func testSellOutcomeClassification() {
        let net = "Error de red."
        func out(_ r: Result<SellResponse, NetworkError>) -> SellOutcome {
            SellOutcome.from(result: r, genericNetwork: net)
        }
        XCTAssertEqual(out(.success(SellResponse(success: true, total: 3, sold: 3))), .total(sold: 3))
        XCTAssertEqual(out(.success(SellResponse(success: true, total: 3, sold: 1))), .partial(sold: 1, total: 3))
        XCTAssertEqual(out(.success(SellResponse(success: true, total: 3, sold: 0))), .none(total: 3))
        XCTAssertEqual(out(.success(SellResponse(success: false, total: 2, sold: 0))), .none(total: 2))
        XCTAssertEqual(out(.failure(.server(500))), .networkError(message: net))
        XCTAssertEqual(out(.failure(.transport("x"))), .networkError(message: net))
    }

    // MARK: - 10. SellResponse decode {success,total,sold,results}

    func testSellResponseDecode() throws {
        let json = #"""
        { "success": true, "total": 2, "sold": 2, "results": [ {"id":"a"}, {"id":"b"} ] }
        """#.data(using: .utf8)!
        let response = try decoder.decode(SellResponse.self, from: json)
        XCTAssertTrue(response.success)
        XCTAssertEqual(response.total, 2)
        XCTAssertEqual(response.sold, 2)

        // Terse body still decodes with defaulted counts.
        let terse = try decoder.decode(SellResponse.self, from: #"{ "success": true }"#.data(using: .utf8)!)
        XCTAssertEqual(terse.total, 0)
        XCTAssertEqual(terse.sold, 0)
    }

    // MARK: - 11. RosterService builds the EXACT backend endpoints (C1)

    func testRosterServiceEndpoints() async throws {
        let rosterJSON = #"""
        [ { "player_id": "a", "name": "A", "slug": "a", "team": "T", "value": 1 } ]
        """#
        let onSaleJSON = #"""
        [ { "player_id": "x", "name": "X", "slug": "x", "team": "T", "value": 2 } ]
        """#

        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: "/api/v1/roster/my", .json(rosterJSON))
        net.setOutcome(pathPrefix: "/api/v1/roster/on-sale", .json(onSaleJSON))
        net.setOutcome(pathPrefix: "/api/v1/roster/sell", .json(#"{ "success": true, "total": 1, "sold": 1 }"#))
        net.setOutcome(pathPrefix: "/api/v1/roster/cancel-sale", .json(#"{ "success": true }"#))
        let service = HTTPRosterService(network: net)

        let roster = try await service.fetchRoster(championshipId: "champ-1")
        XCTAssertEqual(roster.count, 1)
        XCTAssertEqual(net.lastPath(), "/api/v1/roster/my?championship_id=champ-1")

        let onSale = try await service.fetchOnSale(championshipId: "champ-1")
        XCTAssertEqual(onSale.count, 1)
        XCTAssertEqual(net.lastPath(), "/api/v1/roster/on-sale?championship_id=champ-1")

        let sellOutcome = await service.sell(
            championshipId: "champ-1", playerIds: ["a"], genericNetwork: "net"
        )
        XCTAssertEqual(sellOutcome, .total(sold: 1))
        XCTAssertEqual(net.lastPath(), "/api/v1/roster/sell")

        let cancelOutcome = await service.cancelSale(
            championshipId: "champ-1", playerId: "x",
            fallbackRejection: "fb", genericNetwork: "net"
        )
        XCTAssertEqual(cancelOutcome, .accepted)
        XCTAssertEqual(net.lastPath(), "/api/v1/roster/cancel-sale")
    }

    // MARK: - 12. RosterService propagates typed errors without leaking the id

    func testRosterServiceErrorNoLeak() async {
        let net = FakeMarketNetworkClient()
        net.setOutcome(pathPrefix: "/api/v1/roster/my", .failure(.server(503)))
        let service = HTTPRosterService(network: net)
        let secret = "secret-champ-id"
        do {
            _ = try await service.fetchRoster(championshipId: secret)
            XCTFail("Expected throw")
        } catch let error as NetworkError {
            XCTAssertEqual(error, .server(503))
            XCTAssertFalse("\(error)".contains(secret))
        } catch {
            XCTFail("Expected NetworkError")
        }
    }
}
