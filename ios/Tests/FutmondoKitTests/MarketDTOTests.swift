import XCTest
@testable import FutmondoKit

final class MarketDTOTests: XCTestCase {
    private let decoder = JSONDecoder()

    // MARK: - 1. MarketTodayResponse maps snake_case incl. user_info

    func testMarketTodayDecodesPlayersAndUserInfo() throws {
        let json = #"""
        {
          "success": true,
          "players": [
            {
              "player_id": "p-1", "slug": "vinicius-jr", "name": "Vinicius",
              "team": "Real Madrid", "team_logo": "logo.png",
              "position": "fwd", "position2": "mid",
              "value": 80000000, "market_price": 60000000, "change": 2000000,
              "current_bid": null, "current_bid_id": null,
              "average": 7.4, "points": 142, "matches": 20,
              "suggested_bid": 65000000, "sofascore_rating": 7.8,
              "sofascore_url": "https://sofascore/x", "starter_pct": 95,
              "is_favorite": true,
              "photo": "ignored.png", "sofascore_id": 1234
            }
          ],
          "user_info": {
            "balance": 10000000, "team_value": 50000000, "max_bid": 20000000,
            "active_bids_total": 3000000, "available_for_bids": 17000000,
            "active_bids_count": 2
          }
        }
        """#.data(using: .utf8)!

        let response = try decoder.decode(MarketTodayResponse.self, from: json)
        XCTAssertTrue(response.success)
        XCTAssertEqual(response.players.count, 1)

        let player = response.players[0]
        XCTAssertEqual(player.playerId, "p-1")
        XCTAssertEqual(player.id, "p-1")
        XCTAssertEqual(player.slug, "vinicius-jr")
        XCTAssertEqual(player.name, "Vinicius")
        XCTAssertEqual(player.value, 80_000_000)
        XCTAssertEqual(player.marketPrice, 60_000_000)
        XCTAssertEqual(player.suggestedBid, 65_000_000)
        XCTAssertEqual(player.sofascoreRating, 7.8)
        XCTAssertEqual(player.starterPct, 95)
        XCTAssertTrue(player.isFavorite)
        XCTAssertFalse(player.hasActiveBid, "no current_bid → no active bid")

        let info = response.userInfo
        XCTAssertEqual(info.balance, 10_000_000)
        XCTAssertEqual(info.activeBidsTotal, 3_000_000)
        XCTAssertEqual(info.availableForBids, 17_000_000)
    }

    // MARK: - 2. balanceMinusBids derives balance - active_bids_total (W2)

    func testUserInfoBalanceMinusBids() {
        let info = MarketUserInfo(
            balance: 10_000_000,
            teamValue: 0,
            maxBid: 20_000_000,
            activeBidsTotal: 3_000_000,
            availableForBids: 17_000_000
        )
        XCTAssertEqual(info.balanceMinusBids, 7_000_000)

        let negative = MarketUserInfo(
            balance: 1_000_000,
            teamValue: 0,
            maxBid: 0,
            activeBidsTotal: 4_000_000,
            availableForBids: 0
        )
        XCTAssertEqual(negative.balanceMinusBids, -3_000_000, "can go negative (red in UI)")
    }

    // MARK: - 3. Nullable analytics decode to nil (null & absent)

    func testPlayerNullableFieldsDecodeToNil() throws {
        let json = #"""
        {
          "player_id": "p-2", "slug": "s", "name": "N", "team": "T",
          "value": 1000000, "market_price": 500000, "suggested_bid": 600000,
          "change": null, "sofascore_rating": null, "starter_pct": null,
          "average": null, "points": null, "is_favorite": false
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(MarketPlayer.self, from: json)
        XCTAssertNil(player.change)
        XCTAssertNil(player.sofascoreRating)
        XCTAssertNil(player.starterPct)
        XCTAssertNil(player.average)
        XCTAssertNil(player.points)
        XCTAssertNil(player.teamLogo, "absent optional decodes to nil")
    }

    // MARK: - 4. Active bid detection (current_bid + current_bid_id)

    func testPlayerHasActiveBid() throws {
        let json = #"""
        {
          "player_id": "p-3", "slug": "s", "name": "N", "team": "T",
          "value": 1000000, "market_price": 500000, "suggested_bid": 600000,
          "current_bid": 700000, "current_bid_id": "bid-42", "is_favorite": false
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(MarketPlayer.self, from: json)
        XCTAssertTrue(player.hasActiveBid)
        XCTAssertEqual(player.currentBid, 700_000)
        XCTAssertEqual(player.currentBidId, "bid-42")
        XCTAssertEqual(player.activeBidAmount, 700_000)
    }

    /// Angular shows "Puja activa"/"Cancelar" only with `@if (p.current_bid)`,
    /// and the backend emits `current_bid: 0` (NOT null) for no bid — `0` is
    /// falsy in the web view. So `current_bid: 0` must NOT be an active bid.
    func testCurrentBidZeroIsNotAnActiveBid() throws {
        let json = #"""
        {
          "player_id": "p-4", "slug": "s", "name": "N", "team": "T",
          "value": 1000000, "market_price": 500000, "suggested_bid": 600000,
          "current_bid": 0, "current_bid_id": "", "is_favorite": false
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(MarketPlayer.self, from: json)
        XCTAssertFalse(player.hasActiveBid, "current_bid=0 is falsy → no active bid (matches Angular)")
        XCTAssertNil(player.activeBidAmount)
    }

    /// A positive `current_bid` but an empty/missing `current_bid_id` cannot be
    /// cancelled, so it is not treated as an actionable active bid.
    func testPositiveBidWithoutBidIdIsNotActionable() throws {
        let json = #"""
        {
          "player_id": "p-5", "slug": "s", "name": "N", "team": "T",
          "value": 1000000, "market_price": 500000, "suggested_bid": 600000,
          "current_bid": 700000, "current_bid_id": "", "is_favorite": false
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(MarketPlayer.self, from: json)
        XCTAssertFalse(player.hasActiveBid)
        XCTAssertNil(player.activeBidAmount)
    }

    // MARK: - 5. Empty players decodes to an empty list (W1 empty state)

    func testMarketTodayWithEmptyPlayers() throws {
        let json = #"""
        {
          "success": true, "players": [],
          "user_info": { "balance": 0, "team_value": 0, "max_bid": 0,
            "active_bids_total": 0, "available_for_bids": 0 }
        }
        """#.data(using: .utf8)!
        let response = try decoder.decode(MarketTodayResponse.self, from: json)
        XCTAssertTrue(response.players.isEmpty)
    }

    // MARK: - 6. Missing required field fails decoding (strict)

    func testMarketPlayerMissingRequiredFieldThrows() {
        let json = #"""
        { "player_id": "p-1", "slug": "s", "name": "N", "team": "T",
          "market_price": 500000, "suggested_bid": 600000, "is_favorite": false }
        """#.data(using: .utf8)!  // missing value
        XCTAssertThrowsError(try decoder.decode(MarketPlayer.self, from: json))
    }

    // MARK: - 7. SofascoreDetail maps snake_case, sparse row tolerated (W7)

    func testSofascoreDetailDecodesSparseRow() throws {
        let json = #"""
        {
          "player_name": "Vinicius", "rating": 7.8, "goals": 12, "assists": 5,
          "appearances": 20, "matches_started": 19, "starter_pct": 95,
          "minutes_played": 1700, "yellow_cards": 3, "red_cards": 0,
          "tournament": "LaLiga", "season": "24/25",
          "successful_dribbles": 2.3, "accurate_passes_pct": 88.5,
          "shots_on_target": 1.9, "tackles": 0.5, "interceptions": 0.3,
          "clean_sheets": null, "saves": null, "synced_at": "2026-10-20"
        }
        """#.data(using: .utf8)!
        let detail = try decoder.decode(SofascoreDetail.self, from: json)
        XCTAssertEqual(detail.playerName, "Vinicius")
        XCTAssertEqual(detail.rating, 7.8)
        XCTAssertEqual(detail.goals, 12)
        XCTAssertEqual(detail.accuratePassesPct, 88.5)
        XCTAssertNil(detail.cleanSheets)
        XCTAssertNil(detail.saves)
    }

    // MARK: - 8. MarketWriteResponse rejectionMessage prefers message over detail

    func testWriteResponseRejectionMessage() {
        XCTAssertEqual(
            MarketWriteResponse(success: false, message: "Saldo insuficiente", detail: "x").rejectionMessage,
            "Saldo insuficiente"
        )
        XCTAssertEqual(
            MarketWriteResponse(success: false, message: nil, detail: "Equipo no encontrado").rejectionMessage,
            "Equipo no encontrado"
        )
        XCTAssertEqual(
            MarketWriteResponse(success: false, message: "", detail: "fallback").rejectionMessage,
            "fallback",
            "empty message falls through to detail"
        )
        XCTAssertNil(
            MarketWriteResponse(success: true, message: nil, detail: nil).rejectionMessage
        )
    }
}
