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
    // iOS 26 is the device deployment target (F2/D2): the native `TabView` +
    // `Tab` API then renders with the iOS 26 floating "Liquid Glass" tab bar
    // automatically, with no custom effect (Apple SDK only, cost 0 €).
    //
    // This platform list only bounds APPLE builds. On Linux/WSL the host triple
    // is `x86_64-unknown-linux-gnu`, so SwiftPM does not apply the iOS minimum
    // there: `swift build`/`swift test` keep compiling `FutmondoKit` +
    // `FutmondoKitTests` against Foundation, and the SwiftUI app target stays
    // guarded at the source level (`#if canImport(SwiftUI)`), so WSL is
    // unaffected by this bump. The macOS floor stays at 12 for the dev builds.
    platforms: [
        .iOS("26.0"),
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
            path: "Sources/FutmondoApp",
            // F2/iteración 2b: fondo deportivo de la superficie autenticada.
            // `background.jpg` se empaqueta como recurso del target y se carga
            // vía `Bundle.module`. `.process` deja que el toolchain lo optimice
            // donde puede; en WSL el target de app está guardado por
            // `#if canImport(SwiftUI)` y los tests sólo tocan FutmondoKit.
            resources: [
                .process("Resources/background.jpg")
            ]
        ),
        .testTarget(
            name: "FutmondoKitTests",
            dependencies: ["FutmondoKit"],
            path: "Tests/FutmondoKitTests"
        )
    ]
)
