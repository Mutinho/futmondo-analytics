import XCTest
@testable import FutmondoKit

final class BudgetDTOTests: XCTestCase {
    private let decoder = JSONDecoder()

    // MARK: - 1. BalancesResponse maps snake_case and derives ops

    func testBalancesResponseDecodesAndMapsSnakeCase() throws {
        let json = #"""
        {
          "success": true,
          "championship_id": "champ-1",
          "initial_budget": 100000000,
          "teams": [
            {
              "team_id": "t-1",
              "team_name": "Los Galácticos",
              "balance": 12400000,
              "initial_budget": 100000000,
              "total_spent": 50000000,
              "total_income": 30000000,
              "purchases_count": 7,
              "sales_count": 3,
              "team_value": 88000000,
              "performance": 5000000,
              "max_bid": 20000000,
              "prizes": 1500000
            }
          ]
        }
        """#.data(using: .utf8)!

        let response = try decoder.decode(BalancesResponse.self, from: json)
        XCTAssertTrue(response.success)
        XCTAssertEqual(response.championshipId, "champ-1")
        XCTAssertEqual(response.initialBudget, 100_000_000)
        XCTAssertEqual(response.teams.count, 1)

        let team = response.teams[0]
        XCTAssertEqual(team.teamId, "t-1")
        XCTAssertEqual(team.teamName, "Los Galácticos")
        XCTAssertEqual(team.balance, 12_400_000)
        XCTAssertEqual(team.purchasesCount, 7)
        XCTAssertEqual(team.salesCount, 3)
        XCTAssertEqual(team.id, "t-1", "Identifiable id is the team id")
        // Derived property.
        XCTAssertEqual(team.ops, 10, "ops == purchases_count + sales_count")
    }

    // MARK: - 2. Empty teams decodes to an empty list

    func testBalancesResponseWithEmptyTeams() throws {
        let json = #"""
        { "success": true, "championship_id": "c", "initial_budget": 0, "teams": [] }
        """#.data(using: .utf8)!
        let response = try decoder.decode(BalancesResponse.self, from: json)
        XCTAssertTrue(response.teams.isEmpty)
    }

    // MARK: - 3. Missing required field fails decoding (strict decode, SR4)

    func testBalancesResponseMissingRequiredFieldThrows() {
        let json = #"""
        { "success": true, "championship_id": "c", "teams": [] }
        """#.data(using: .utf8)!  // missing initial_budget
        XCTAssertThrowsError(try decoder.decode(BalancesResponse.self, from: json))
    }

    // MARK: - 4. ChampionshipsResponse WITH optional extras present

    func testChampionshipsResponseWithExtras() throws {
        let json = #"""
        {
          "success": true,
          "championships": [
            {
              "championship_id": "champ-1",
              "name": "Liga Pro",
              "initial_budget": 100000000,
              "has_clauses": true,
              "excluded_teams": ["t-9"],
              "money_per_point": 50000,
              "money_per_ranking": 20000,
              "dream_team_bonus": 1000000,
              "mvp_bonus": 500000,
              "ranking_mode": "proportional",
              "users_to_rank": 8
            }
          ]
        }
        """#.data(using: .utf8)!

        let response = try decoder.decode(ChampionshipsResponse.self, from: json)
        XCTAssertEqual(response.championships.count, 1)
        let champ = response.championships[0]
        XCTAssertEqual(champ.championshipId, "champ-1")
        XCTAssertEqual(champ.id, "champ-1")
        XCTAssertTrue(champ.hasClauses)
        XCTAssertEqual(champ.excludedTeams, ["t-9"])
        XCTAssertEqual(champ.moneyPerPoint, 50_000)
        XCTAssertEqual(champ.rankingMode, "proportional")
        XCTAssertEqual(champ.usersToRank, 8)
    }

    // MARK: - 5. ChampionshipsResponse WITHOUT optional extras (legacy subset)

    func testChampionshipsResponseWithoutExtras() throws {
        let json = #"""
        {
          "success": true,
          "championships": [
            {
              "championship_id": "champ-legacy",
              "name": "Liga Legacy",
              "initial_budget": 80000000,
              "has_clauses": false,
              "excluded_teams": []
            }
          ]
        }
        """#.data(using: .utf8)!

        let response = try decoder.decode(ChampionshipsResponse.self, from: json)
        let champ = response.championships[0]
        XCTAssertEqual(champ.championshipId, "champ-legacy")
        XCTAssertFalse(champ.hasClauses)
        XCTAssertTrue(champ.excludedTeams.isEmpty)
        // All optional extras absent → nil, no decode failure.
        XCTAssertNil(champ.moneyPerPoint)
        XCTAssertNil(champ.moneyPerRanking)
        XCTAssertNil(champ.dreamTeamBonus)
        XCTAssertNil(champ.mvpBonus)
        XCTAssertNil(champ.rankingMode)
        XCTAssertNil(champ.usersToRank)
    }

    // MARK: - 6. TeamDetailResponse maps snake_case incl. optional from/to (FR6)

    func testTeamDetailResponseDecodesWithOptionalFromTo() throws {
        let json = #"""
        {
          "success": true,
          "team_id": "t-1",
          "team_name": "Los Galácticos",
          "balance": 12400000,
          "initial_budget": 100000000,
          "total_spent": 50000000,
          "total_income": 30000000,
          "purchases": [
            {
              "player_id": "p-1", "player_name": "Vinicius", "price": 20000000,
              "date": "2026-01-15", "from": "Computer"
            }
          ],
          "sales": [
            {
              "player_id": "p-2", "player_name": "Modric", "price": 8000000,
              "date": "2026-02-01", "to": "Computer"
            }
          ]
        }
        """#.data(using: .utf8)!

        let response = try decoder.decode(TeamDetailResponse.self, from: json)
        XCTAssertTrue(response.success)
        XCTAssertEqual(response.teamId, "t-1")
        XCTAssertEqual(response.teamName, "Los Galácticos")
        XCTAssertEqual(response.balance, 12_400_000)
        XCTAssertEqual(response.initialBudget, 100_000_000)
        XCTAssertEqual(response.totalSpent, 50_000_000)
        XCTAssertEqual(response.totalIncome, 30_000_000)

        XCTAssertEqual(response.purchases.count, 1)
        let purchase = response.purchases[0]
        XCTAssertEqual(purchase.playerId, "p-1")
        XCTAssertEqual(purchase.playerName, "Vinicius")
        XCTAssertEqual(purchase.price, 20_000_000)
        XCTAssertEqual(purchase.date, "2026-01-15")
        // A purchase carries `from` (procedencia) and no `to`.
        XCTAssertEqual(purchase.from, "Computer")
        XCTAssertNil(purchase.to)
        XCTAssertEqual(purchase.id, "p-1#2026-01-15")

        XCTAssertEqual(response.sales.count, 1)
        let sale = response.sales[0]
        XCTAssertEqual(sale.playerId, "p-2")
        // A sale carries `to` (destino) and no `from`.
        XCTAssertEqual(sale.to, "Computer")
        XCTAssertNil(sale.from)
    }

    // MARK: - 7. TeamDetailResponse with empty purchases/sales lists

    func testTeamDetailResponseWithEmptyLists() throws {
        let json = #"""
        {
          "success": true, "team_id": "t-9", "team_name": "Sin fichajes",
          "balance": 0, "initial_budget": 0, "total_spent": 0,
          "total_income": 0, "purchases": [], "sales": []
        }
        """#.data(using: .utf8)!
        let response = try decoder.decode(TeamDetailResponse.self, from: json)
        XCTAssertTrue(response.purchases.isEmpty)
        XCTAssertTrue(response.sales.isEmpty)
    }

    // MARK: - 8. TeamDetailResponse missing required field fails decoding (SR4)

    func testTeamDetailResponseMissingRequiredFieldThrows() {
        let json = #"""
        {
          "success": true, "team_id": "t-1", "team_name": "X",
          "balance": 0, "initial_budget": 0, "total_spent": 0,
          "purchases": [], "sales": []
        }
        """#.data(using: .utf8)!  // missing total_income
        XCTAssertThrowsError(try decoder.decode(TeamDetailResponse.self, from: json))
    }
}
