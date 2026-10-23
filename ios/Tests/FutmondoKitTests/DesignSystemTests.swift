import XCTest
@testable import FutmondoKit

/// Pure-logic tests for the design-system color tokens. Covers appearance
/// resolution (BR1.1) and role coverage (FR1). SwiftUI views are validated on
/// device, not here.
final class DesignSystemColorTests: XCTestCase {

    /// Case 1 — `DSColorValue` resolves the light value in `.light` and the
    /// dark value in `.dark`. [BR1.1]
    func testColorValueResolvesByAppearance() {
        let value = DSColorValue(lightHex: "#2E7D32", darkHex: "#66BB6A")
        XCTAssertEqual(value.hex(for: .light), "#2E7D32")
        XCTAssertEqual(value.hex(for: .dark), "#66BB6A")
    }

    /// Case 1 (token level) — the `primary` role resolves to the Angular green
    /// in each appearance. [BR1.1, FR1]
    func testPrimaryTokenResolvesByAppearance() {
        XCTAssertEqual(DSColorToken.primary.value.hex(for: .light), "#2E7D32")
        XCTAssertEqual(DSColorToken.primary.value.hex(for: .dark), "#66BB6A")
    }

    /// Case 2 — every color role defines both a light and a dark variant, and
    /// both parse as valid `#RRGGBB`. [FR1]
    func testEveryRoleHasLightAndDarkVariant() {
        for token in DSColorToken.allCases {
            let light = token.value.rgb(for: .light)
            let dark = token.value.rgb(for: .dark)
            XCTAssertNotNil(light, "\(token.rawValue) light hex is malformed")
            XCTAssertNotNil(dark, "\(token.rawValue) dark hex is malformed")
            XCTAssertNotEqual(
                token.value.lightHex, "",
                "\(token.rawValue) must define a light value"
            )
            XCTAssertNotEqual(
                token.value.darkHex, "",
                "\(token.rawValue) must define a dark value"
            )
        }
        // The contract surface guarantees exactly these eleven roles.
        XCTAssertEqual(DSColorToken.allCases.count, 11)
    }

    /// Hex parsing rejects malformed input (fail loud, not silent coercion).
    func testHexParsingRejectsMalformedInput() {
        XCTAssertNil(DSRGB(hex: "#12"))
        XCTAssertNil(DSRGB(hex: "#GGGGGG"))
        XCTAssertNil(DSRGB(hex: "zzz"))
        let white = DSRGB(hex: "#FFFFFF")
        XCTAssertEqual(white, DSRGB(red: 255, green: 255, blue: 255))
    }

    /// The splash gradient exposes its three ordered stops. [FR1.3]
    func testSplashGradientStops() {
        XCTAssertEqual(DSSplashGradient.stops, ["#1B5E20", "#2E7D32", "#43A047"])
    }
}

/// Pure-logic tests for the spacing scale. [FR3]
final class DesignSystemSpacingTests: XCTestCase {

    /// Case 3 — the spacing scale returns 4/8/16/24/32 for xs/sm/md/lg/xl. [FR3]
    func testSpacingScaleValues() {
        XCTAssertEqual(DSSpacing.xs.points, 4)
        XCTAssertEqual(DSSpacing.sm.points, 8)
        XCTAssertEqual(DSSpacing.md.points, 16)
        XCTAssertEqual(DSSpacing.lg.points, 24)
        XCTAssertEqual(DSSpacing.xl.points, 32)
        XCTAssertEqual(DSSpacing.allCases.count, 5)
    }

    /// The scale is strictly increasing (sanity on ordering).
    func testSpacingScaleIsMonotonic() {
        let ordered = DSSpacing.allCases.map(\.points)
        XCTAssertEqual(ordered, ordered.sorted())
    }
}

/// Pure-logic tests for the typography scale. [FR2]
final class DesignSystemTypographyTests: XCTestCase {

    /// Case 4 — the typography scale returns base sizes h1=28/h2=20/h3=16/
    /// body=14. [FR2]
    func testTypographyBaseSizes() {
        XCTAssertEqual(DSTypographyScale.h1.baseSize, 28)
        XCTAssertEqual(DSTypographyScale.h2.baseSize, 20)
        XCTAssertEqual(DSTypographyScale.h3.baseSize, 16)
        XCTAssertEqual(DSTypographyScale.body.baseSize, 14)
        XCTAssertEqual(DSTypographyScale.allCases.count, 4)
    }

    /// Each role carries the Angular-mirroring weight, and the preferred family
    /// is Roboto (the accessor falls back to the system font). [BR1.3]
    func testTypographyWeightsAndFamily() {
        XCTAssertEqual(DSTypographyScale.h1.weight, .bold)
        XCTAssertEqual(DSTypographyScale.h2.weight, .semibold)
        XCTAssertEqual(DSTypographyScale.h3.weight, .semibold)
        XCTAssertEqual(DSTypographyScale.body.weight, .regular)
        XCTAssertEqual(DSTypographyScale.preferredFontFamily, "Roboto")
    }
}

/// Pure-logic tests for the WCAG contrast helper. [BR1.4, NFR1]
final class DesignSystemContrastTests: XCTestCase {

    /// Reference pairs from WCAG: black on white is the maximum 21:1, and a
    /// color against itself is the minimum 1:1.
    func testContrastReferencePairs() {
        let white = DSRGB(hex: "#FFFFFF")!
        let black = DSRGB(hex: "#000000")!
        XCTAssertEqual(ContrastRatio.ratio(white, black), 21.0, accuracy: 0.01)
        XCTAssertEqual(ContrastRatio.ratio(white, white), 1.0, accuracy: 0.0001)
    }

    /// Case 5 — normal text (`onSurface`) over `surface` meets ≥4.5:1 in both
    /// light and dark. [BR1.4, NFR1]
    func testOnSurfaceMeetsNormalTextContrast() {
        for appearance in DSAppearance.allCases {
            XCTAssertTrue(
                ContrastRatio.meets(
                    .onSurface, on: .surface,
                    appearance: appearance,
                    threshold: ContrastRatio.normalTextThreshold
                ),
                "onSurface/surface must meet 4.5:1 in \(appearance)"
            )
        }
    }

    /// Case 6 — the money semantic colors over `surface` meet at least the
    /// ≥3:1 UI target (and, as measured, the ≥4.5:1 text target too). [BR1.4]
    func testMoneyColorsMeetContrast() {
        for appearance in DSAppearance.allCases {
            for token in [DSColorToken.moneyPositive, .moneyNegative] {
                let value = ContrastRatio.ratio(token, on: .surface, appearance: appearance)
                XCTAssertNotNil(value)
                XCTAssertGreaterThanOrEqual(
                    value!, ContrastRatio.largeTextThreshold,
                    "\(token.rawValue)/surface must meet 3:1 in \(appearance)"
                )
                // Measured values clear the stricter normal-text target as well.
                XCTAssertGreaterThanOrEqual(
                    value!, ContrastRatio.normalTextThreshold,
                    "\(token.rawValue)/surface meets 4.5:1 in \(appearance)"
                )
            }
        }
    }

    /// Case 7 (edge) — an intentionally insufficient pair (light gray on white)
    /// is detected as failing the normal-text target. [BR1.4]
    func testInsufficientContrastIsDetected() {
        let lightGray = DSRGB(hex: "#AAAAAA")!
        let white = DSRGB(hex: "#FFFFFF")!
        let value = ContrastRatio.ratio(lightGray, white)
        XCTAssertLessThan(value, ContrastRatio.normalTextThreshold)
    }

    /// The whole declared palette's text/UI pairs against `surface` clear the
    /// contrast targets — guards the token table against a regression that
    /// would need a value adjustment rather than a lowered threshold. [BR1.4]
    func testDeclaredTextRolesMeetTargets() {
        // (foreground, threshold) pairs validated against surface.
        let checks: [(DSColorToken, Double)] = [
            (.onSurface, ContrastRatio.normalTextThreshold),
            (.onSurfaceVariant, ContrastRatio.normalTextThreshold),
            (.primary, ContrastRatio.largeTextThreshold),
        ]
        for appearance in DSAppearance.allCases {
            for (token, threshold) in checks {
                XCTAssertTrue(
                    ContrastRatio.meets(
                        token, on: .surface,
                        appearance: appearance, threshold: threshold
                    ),
                    "\(token.rawValue)/surface below \(threshold) in \(appearance)"
                )
            }
        }
    }

    /// Iteración 2c — every text colour rendered on the dark neon-glass budget
    /// card (SALDO green, PREMIOS blue, white values/name, grey stat labels,
    /// and the negative-performance red) meets the ≥4.5:1 normal-text target
    /// against the `cardSurfaceDark` baseline (the opaque approximation of the
    /// black-0.45-over-material glass). This is the testable part of the
    /// owner's contrast requirement; the translucent render is device-validated.
    /// If a pure neon failed here, the surface would be darkened or the text
    /// lightened — never the threshold lowered. [BR1.4, NFR1, NFR5]
    func testDarkNeonGlassCardTextMeetsContrast() {
        // (role, human description) — all resolved for the dark appearance,
        // which is the only one the dark-forced app renders.
        let cardTextRoles: [(DSColorToken, String)] = [
            (.onSurface, "team name + PUJA MÁXIMA (white)"),
            (.onSurfaceVariant, "uppercase stat labels (grey)"),
            (.moneyPositive, "SALDO + positive RENDIMIENTO (green)"),
            (.moneyNegative, "negative RENDIMIENTO (red)"),
            (.moneyPrize, "PREMIOS (blue)"),
        ]
        for (token, description) in cardTextRoles {
            let value = ContrastRatio.ratio(token, on: .cardSurfaceDark, appearance: .dark)
            XCTAssertNotNil(value, "\(description) contrast must be computable")
            XCTAssertGreaterThanOrEqual(
                value!, ContrastRatio.normalTextThreshold,
                "\(description) must meet 4.5:1 on the dark neon-glass card "
                + "(measured \(value ?? 0))"
            )
        }
    }
}
