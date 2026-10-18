import SwiftUI

/// Entry point of the xtool spike app.
///
/// This is the smallest SwiftUI application that still produces a visible,
/// launchable screen on the device. Its only purpose is to be the payload that
/// travels the full xtool chain: build -> free signing -> install -> launch.
@main
struct XToolSpikeApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
