// swift-tools-version: 6.0
// Minimal SwiftPM manifest for the xtool toolchain spike (B-01).
// An xtool project must expose EXACTLY ONE library product representing the
// main app (xtool packages that library into the iOS .app). Kept intentionally
// minimal: no extra dependencies, no extensions, no test targets (the spike's
// acceptance is a manual on-device smoke, not an automated suite).
import PackageDescription

let package = Package(
    name: "XToolSpike",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    products: [
        // Exactly one library product, representing the main app (xtool contract).
        .library(
            name: "XToolSpike",
            targets: ["XToolSpike"]
        ),
    ],
    targets: [
        .target(
            name: "XToolSpike"
        ),
    ]
)
