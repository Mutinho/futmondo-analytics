// swift-tools-version:6.0
// FutmondoKit — native networking + auth layer for the Futmondo Analytics iOS app (F1).
// Apple SDK only: zero external SwiftPM dependencies (NFR-2 / P-3).
//
// Target layout (Bolt 3):
// - `FutmondoKit` (library): device-independent, testable logic — networking
//   (Bolt 2) and auth (`AuthService`, DTOs, `TokenHolder`, `KeychainStore` +
//   its in-memory double). The real `KeychainTokenStore` is guarded with
//   `#if canImport(Security)`, so this library compiles on Linux/WSL.
// - `FutmondoApp` (executable): the SwiftUI app shell (`AuthViewModel`,
//   `LoginView`, `SplashView`, `@main FutmondoApp`). SwiftUI does NOT exist on
//   Linux; every file is guarded with `#if canImport(SwiftUI)`. It is a
//   separate target that the test target does NOT depend on, so
//   `swift test` on Linux/WSL compiles only `FutmondoKit` + `FutmondoKitTests`
//   and never pulls in SwiftUI.
// - `FutmondoKitTests`: XCTest over `FutmondoKit` only.
import PackageDescription

let package = Package(
    name: "FutmondoKit",
    // Reasonable minimums so `swift test` compiles on Linux/WSL against Foundation,
    // while keeping the device targets (iPhone 13 Pro) in range. The SwiftUI
    // views require iOS 17 / macOS 14 and are guarded at the source level.
    platforms: [
        .iOS(.v15),
        .macOS(.v12)
    ],
    products: [
        .library(
            name: "FutmondoKit",
            targets: ["FutmondoKit"]
        ),
        // xtool packages a LIBRARY product into the iOS .app (xtool contract:
        // the app product is a library, not an executable). `xtool.yml` points
        // `product: FutmondoApp` here. SwiftUI is guarded at the source level,
        // so on Linux/WSL this target compiles to (essentially) empty and
        // `swift test` (which depends only on FutmondoKit) never pulls SwiftUI.
        .library(
            name: "FutmondoApp",
            targets: ["FutmondoApp"]
        )
    ],
    dependencies: [],
    targets: [
        .target(
            name: "FutmondoKit",
            dependencies: [],
            path: "Sources/FutmondoKit"
        ),
        .target(
            name: "FutmondoApp",
            dependencies: ["FutmondoKit"],
            path: "Sources/FutmondoApp"
        ),
        .testTarget(
            name: "FutmondoKitTests",
            dependencies: ["FutmondoKit"],
            path: "Tests/FutmondoKitTests"
        )
    ]
)
