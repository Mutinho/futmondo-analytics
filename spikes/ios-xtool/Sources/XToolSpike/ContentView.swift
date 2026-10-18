import SwiftUI

/// Trivial view used as visual boot evidence for the spike.
///
/// If this screen renders on the iPhone, the whole xtool chain (build, free
/// signing, install, launch) succeeded. It shows a fixed marker string plus the
/// bundle short version so a screenshot doubles as proof of which build ran.
struct ContentView: View {
    /// App version string read from the bundle (CFBundleShortVersionString),
    /// falling back to "unknown" so the view never crashes if the key is absent.
    private var appVersion: String {
        let shortVersion = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String
        return shortVersion ?? "unknown"
    }

    var body: some View {
        VStack(spacing: 12) {
            // Fixed marker: a human reading the device screen confirms success.
            Text("xtool OK")
                .font(.largeTitle)
                .bold()

            // Version string ties the screenshot to a specific build.
            Text("version \(appVersion)")
                .font(.body)
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
