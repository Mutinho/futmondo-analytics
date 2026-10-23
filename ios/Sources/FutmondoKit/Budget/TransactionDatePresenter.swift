import Foundation

/// Deterministic, locale-independent date presenter for the team-detail rows
/// (FR6): maps an ISO `yyyy-MM-dd` (optionally with a `T`/space time suffix) to
/// `dd/MM/yyyy`. Falls back to the raw string when the prefix does not parse,
/// so a format surprise never breaks a row. Pure string work — no
/// `DateFormatter`, no locale — so it behaves identically on WSL and device,
/// and it lives in `FutmondoKit` so it is unit-testable with XCTest in WSL.
public enum TransactionDatePresenter {
    /// Render the ISO date `iso` as `dd/MM/yyyy`, or return `iso` unchanged when
    /// its leading date part is not a well-formed `yyyy-MM-dd`.
    public static func display(_ iso: String) -> String {
        // Take the date part before any `T`/space time separator.
        let datePart = iso.prefix { $0 != "T" && $0 != " " }
        let components = datePart.split(separator: "-")
        guard components.count == 3,
              components[0].count == 4,
              (1...2).contains(components[1].count),
              (1...2).contains(components[2].count),
              components.allSatisfy({ $0.allSatisfy(\.isNumber) }) else {
            return iso
        }
        let year = String(components[0])
        let month = components[1].count == 1 ? "0\(components[1])" : String(components[1])
        let day = components[2].count == 1 ? "0\(components[2])" : String(components[2])
        return "\(day)/\(month)/\(year)"
    }
}
