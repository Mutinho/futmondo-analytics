import XCTest
@testable import FutmondoKit

/// Tests for `MarketImageURL` (FR4): player photo / team logo URL building,
/// reproducing the Angular `player.utils.ts` bases, with empty-value fallbacks.
final class MarketImageURLTests: XCTestCase {

    func testPlayerPhotoURLFromSlug() {
        let url = MarketImageURL.playerPhoto(slug: "lionel-messi")
        XCTAssertEqual(
            url?.absoluteString,
            "https://static01.mondocore.com/futmondo/img/faces/64/lionel-messi.png"
        )
    }

    func testPlayerPhotoNilForEmptySlug() {
        XCTAssertNil(MarketImageURL.playerPhoto(slug: ""))
        XCTAssertNil(MarketImageURL.playerPhoto(slug: "   "))
    }

    func testTeamLogoURLFromValue() {
        let url = MarketImageURL.teamLogo("barcelona.png")
        XCTAssertEqual(
            url?.absoluteString,
            "https://static02.mondocore.com/futmondo/img/teams/64/barcelona.png"
        )
    }

    func testTeamLogoNilForEmptyOrMissing() {
        XCTAssertNil(MarketImageURL.teamLogo(nil))
        XCTAssertNil(MarketImageURL.teamLogo(""))
        XCTAssertNil(MarketImageURL.teamLogo("  "))
    }

    func testBasesAreHTTPS() {
        XCTAssertTrue(MarketImageURL.photoBase.hasPrefix("https://"))
        XCTAssertTrue(MarketImageURL.teamLogoBase.hasPrefix("https://"))
    }
}
