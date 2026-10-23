import Foundation

/// Pure, testable in-memory freshness policy shared by the screen view models
/// so switching tabs does NOT refetch from the API every time.
///
/// It records which championship's data was last loaded and when. A view model
/// asks `shouldReload(activeId:now:)` before loading: it returns `true` only
/// when there is no cached load, the active championship changed, or the cached
/// data is older than `ttl`. Explicit refresh (pull-to-refresh), a championship
/// switch, and post-write reloads bypass this by calling the hard load directly
/// or by `invalidate()`.
///
/// SwiftUI/UIKit-free and deterministic (`now` is injected), so it is covered
/// by `swift test` on Linux/WSL.
public struct DataFreshness: Sendable, Equatable {
    /// Default time-to-live before cached data is considered stale (3 minutes).
    public static let defaultTTL: TimeInterval = 180

    private let ttl: TimeInterval
    private var lastLoadedChampionshipId: String?
    private var lastLoadedAt: Date?

    public init(ttl: TimeInterval = DataFreshness.defaultTTL) {
        self.ttl = ttl
    }

    /// Whether a (re)load is needed for `activeId` at time `now`.
    ///
    /// Reloads when: never loaded, the active championship differs from the one
    /// cached, or the cached load is older than `ttl`. A `nil`/empty `activeId`
    /// always reloads (there is nothing meaningful cached to show).
    public func shouldReload(activeId: String?, now: Date = Date()) -> Bool {
        guard let activeId, !activeId.isEmpty else { return true }
        guard let lastLoadedChampionshipId, let lastLoadedAt else { return true }
        if lastLoadedChampionshipId != activeId { return true }
        return now.timeIntervalSince(lastLoadedAt) >= ttl
    }

    /// Record a successful load of `championshipId` at `now`, so subsequent
    /// `shouldReload` calls within the TTL (and same championship) return false.
    public mutating func markLoaded(championshipId: String, now: Date = Date()) {
        lastLoadedChampionshipId = championshipId
        lastLoadedAt = now
    }

    /// Drop the cached marker so the next `shouldReload` returns true (used for
    /// cross-screen invalidation after a write that changes shared figures).
    public mutating func invalidate() {
        lastLoadedChampionshipId = nil
        lastLoadedAt = nil
    }
}
