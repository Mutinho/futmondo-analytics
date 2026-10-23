import Foundation

/// Player photo / team logo URL builder (FR4), reproducing the Angular
/// `player.utils.ts` helpers as the design source of truth:
/// `PHOTO_BASE = https://static01.mondocore.com/futmondo/img/faces/64/{slug}.png`
/// and `TEAM_LOGO_BASE = https://static02.mondocore.com/futmondo/img/teams/64/{team_logo}`.
///
/// Pure and `FutmondoKit`-side so it is unit-tested; the SwiftUI card feeds the
/// resulting `URL` to `AsyncImage` and falls back to a grey silhouette when the
/// slug/logo is empty or the image fails to load (mirroring Angular's
/// `onImgError` default avatar).
public enum MarketImageURL {
    /// HTTPS base for 64px player face photos.
    public static let photoBase = "https://static01.mondocore.com/futmondo/img/faces/64/"
    /// HTTPS base for 64px team logos.
    public static let teamLogoBase = "https://static02.mondocore.com/futmondo/img/teams/64/"

    /// The player photo URL for a slug, or `nil` when the slug is empty (the UI
    /// then shows the silhouette placeholder, as Angular's default avatar does).
    public static func playerPhoto(slug: String) -> URL? {
        let trimmed = slug.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        return URL(string: photoBase + trimmed + ".png")
    }

    /// The team logo URL for a `team_logo` value, or `nil` when it is empty
    /// (Angular returns `''` → no image). The value already carries its own
    /// extension on the wire, so it is appended verbatim.
    public static func teamLogo(_ logo: String?) -> URL? {
        guard let logo else { return nil }
        let trimmed = logo.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        return URL(string: teamLogoBase + trimmed)
    }
}
