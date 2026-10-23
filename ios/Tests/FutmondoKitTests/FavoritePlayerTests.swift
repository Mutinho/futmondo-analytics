import XCTest
@testable import FutmondoKit

final class FavoritePlayerTests: XCTestCase {
    private let decoder = JSONDecoder()

    // MARK: - 1. FavoritePlayer maps snake_case incl. home/away/rating

    func testFavoritePlayerDecodesSnakeCase() throws {
        let json = #"""
        {
          "player_id": "p-1", "name": "Vinicius", "slug": "vinicius-jr",
          "position": "Delantero", "position2": "Medio",
          "team": "Real Madrid", "team_logo": "rm.png",
          "value": 80000000, "change": 150000, "points": 142,
          "average": 7.4, "home_average": 7.9, "away_average": 6.8, "matches": 20,
          "rating": 7.1, "sofascore_rating": 7.8,
          "sofascore_url": "https://sofascore/x",
          "starter_pct": 95, "status": "ok",
          "ignored_extra": true
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(FavoritePlayer.self, from: json)
        XCTAssertEqual(player.playerId, "p-1")
        XCTAssertEqual(player.id, "p-1")
        XCTAssertEqual(player.name, "Vinicius")
        XCTAssertEqual(player.slug, "vinicius-jr")
        XCTAssertEqual(player.value, 80_000_000)
        XCTAssertEqual(player.change, 150_000)
        XCTAssertEqual(player.points, 142)
        XCTAssertEqual(player.average, 7.4)
        XCTAssertEqual(player.homeAverage, 7.9)
        XCTAssertEqual(player.awayAverage, 6.8)
        XCTAssertEqual(player.matches, 20)
        XCTAssertEqual(player.teamLogo, "rm.png")
        XCTAssertEqual(player.starterPct, 95)
        XCTAssertEqual(player.status, "ok")
    }

    // MARK: - 2. The TWO ratings decode independently (BR3.3)

    func testFavoritePlayerHasTwoIndependentRatings() throws {
        let json = #"""
        {
          "player_id": "p-2", "name": "N", "slug": "s", "team": "T",
          "value": 1000000, "rating": 6.4, "sofascore_rating": 7.2
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(FavoritePlayer.self, from: json)
        // `rating` is decoded but never shown; `sofascore_rating` drives badge
        // + sort. They are distinct fields with distinct values (BR3.3).
        XCTAssertEqual(player.rating, 6.4)
        XCTAssertEqual(player.sofascoreRating, 7.2)
    }

    // MARK: - 3. `rating` is tolerant: absent → nil (decodeIfPresent)

    func testFavoritePlayerRatingTolerantWhenAbsent() throws {
        let json = #"""
        {
          "player_id": "p-3", "name": "N", "slug": "s", "team": "T",
          "value": 1000000, "sofascore_rating": 7.0
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(FavoritePlayer.self, from: json)
        XCTAssertNil(player.rating, "absent `rating` decodes to nil (tolerant page-decode)")
        XCTAssertEqual(player.sofascoreRating, 7.0)
    }

    // MARK: - 4. Nullable analytics decode to nil (null & absent)

    func testFavoritePlayerNullableFieldsDecodeToNil() throws {
        let json = #"""
        {
          "player_id": "p-4", "name": "N", "slug": "s", "team": "T",
          "value": 1000000,
          "change": null, "points": null, "average": null,
          "home_average": null, "away_average": null, "matches": null,
          "rating": null, "sofascore_rating": null, "starter_pct": null
        }
        """#.data(using: .utf8)!
        let player = try decoder.decode(FavoritePlayer.self, from: json)
        XCTAssertNil(player.change)
        XCTAssertNil(player.points)
        XCTAssertNil(player.average)
        XCTAssertNil(player.homeAverage)
        XCTAssertNil(player.awayAverage)
        XCTAssertNil(player.matches)
        XCTAssertNil(player.rating)
        XCTAssertNil(player.sofascoreRating)
        XCTAssertNil(player.starterPct)
        XCTAssertNil(player.sofascoreUrl, "absent optional decodes to nil")
    }

    // MARK: - 5. Missing required field fails decoding (strict)

    func testFavoritePlayerMissingValueThrows() {
        let json = #"""
        { "player_id": "p-1", "name": "N", "slug": "s", "team": "T" }
        """#.data(using: .utf8)!  // missing value
        XCTAssertThrowsError(try decoder.decode(FavoritePlayer.self, from: json))
    }

    // MARK: - 6. FavoritesResponse tolerates root-array shape

    func testFavoritesResponseRootArray() throws {
        let json = #"""
        [
          { "player_id": "a", "name": "A", "slug": "a", "team": "T", "value": 1 },
          { "player_id": "b", "name": "B", "slug": "b", "team": "T", "value": 2 }
        ]
        """#.data(using: .utf8)!
        let response = try decoder.decode(FavoritesResponse.self, from: json)
        XCTAssertEqual(response.players.map(\.playerId), ["a", "b"])
    }

    // MARK: - 7. FavoritesResponse tolerates wrapped shapes (`players` / `favorites`)

    func testFavoritesResponseWrappedPlayers() throws {
        let json = #"""
        { "players": [ { "player_id": "a", "name": "A", "slug": "a", "team": "T", "value": 1 } ] }
        """#.data(using: .utf8)!
        let response = try decoder.decode(FavoritesResponse.self, from: json)
        XCTAssertEqual(response.players.count, 1)
    }

    func testFavoritesResponseWrappedFavorites() throws {
        let json = #"""
        { "favorites": [ { "player_id": "z", "name": "Z", "slug": "z", "team": "T", "value": 9 } ] }
        """#.data(using: .utf8)!
        let response = try decoder.decode(FavoritesResponse.self, from: json)
        XCTAssertEqual(response.players.map(\.playerId), ["z"])
    }

    // MARK: - 8. An empty wrapped body decodes to an empty list

    func testFavoritesResponseEmptyWrapped() throws {
        let json = #"{ "success": true }"#.data(using: .utf8)!
        let response = try decoder.decode(FavoritesResponse.self, from: json)
        XCTAssertTrue(response.players.isEmpty)
    }
}
