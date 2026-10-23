import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// Developer catalog for visually verifying the design system against the
/// Angular theme (W1). Shows the sections in order Colors → Typography →
/// Spacing → Components, with a theme toggle (light/dark) and a text-size
/// control that exercise BR1.1 and BR1.2. [FR5]
@available(iOS 16.0, macOS 13.0, *)
public struct CatalogView: View {
    @State private var forcedDark = false
    @State private var textSize: DynamicTypeSize = .large

    public init() {}

    public var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.lg) {
                controls
                colorsSection
                typographySection
                spacingSection
                componentsSection
            }
            .padding(DSSpacingSwiftUI.md)
        }
        .background(DSColor.surface)
        .environment(\.colorScheme, forcedDark ? .dark : .light)
        .environment(\.dynamicTypeSize, textSize)
        .accessibilityIdentifier("catalog-view")
    }

    // MARK: - Controls

    private var controls: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
            ThemeToggle(isDark: $forcedDark)
            TextSizeControl(size: $textSize)
        }
    }

    // MARK: - Sections

    private var colorsSection: some View {
        section("Colors") {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
                ForEach(DSColorToken.allCases, id: \.rawValue) { token in
                    HStack(spacing: DSSpacingSwiftUI.sm) {
                        RoundedRectangle(cornerRadius: 6)
                            .fill(DSColor.color(token))
                            .frame(width: 44, height: 44)
                            .overlay(
                                RoundedRectangle(cornerRadius: 6)
                                    .stroke(DSColor.onSurfaceVariant.opacity(0.3))
                            )
                        Text(token.rawValue)
                            .font(DSFont.body)
                            .foregroundStyle(DSColor.onSurface)
                    }
                }
                RoundedRectangle(cornerRadius: 8)
                    .fill(DSColor.splashGradient)
                    .frame(height: 44)
                    .overlay(Text("splashGradient").font(DSFont.body).foregroundStyle(.white))
            }
        }
    }

    private var typographySection: some View {
        section("Typography") {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
                Text("h1 — Título").font(DSFont.h1)
                Text("h2 — Subtítulo").font(DSFont.h2)
                Text("h3 — Encabezado").font(DSFont.h3)
                Text("body — Texto base").font(DSFont.body)
            }
            .foregroundStyle(DSColor.onSurface)
        }
    }

    private var spacingSection: some View {
        section("Spacing") {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
                ForEach(DSSpacing.allCases, id: \.rawValue) { step in
                    HStack(spacing: DSSpacingSwiftUI.sm) {
                        Rectangle()
                            .fill(DSColor.primary)
                            .frame(width: DSSpacingSwiftUI.value(step), height: 16)
                        Text("\(step.rawValue) = \(Int(step.points))")
                            .font(DSFont.body)
                            .foregroundStyle(DSColor.onSurface)
                    }
                }
            }
        }
    }

    private var componentsSection: some View {
        section("Components") {
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.md) {
                PrimaryButton(title: "Normal", action: {})
                PrimaryButton(title: "Loading", isLoading: true, action: {})
                PrimaryButton(title: "Disabled", isEnabled: false, action: {})
                TextInputField(
                    label: "Email",
                    text: .constant("javi@example.com"),
                    icon: Image(systemName: "envelope")
                )
                TextInputField(
                    label: "Contraseña",
                    text: .constant("secret"),
                    icon: Image(systemName: "lock"),
                    isSecure: true
                )
                TextInputField(
                    label: "Con error",
                    text: .constant("x"),
                    errorMessage: "Campo obligatorio"
                )
                Card { Text("Card de ejemplo").font(DSFont.body).foregroundStyle(DSColor.onSurface) }
                ElevatedCard { Text("ElevatedCard (sombra suave)").font(DSFont.body).foregroundStyle(DSColor.onSurface) }
                HStack(spacing: DSSpacingSwiftUI.sm) {
                    DSChip(systemImage: "trophy", text: "Campeonato")
                    DSChip(systemImage: "arrow.up.arrow.down", text: "Ordenar por: Saldo")
                    DSChip(text: "Vacío", showsChevron: false, isEnabled: false)
                }
                HStack(spacing: DSSpacingSwiftUI.sm) {
                    DSMoneyBadge(value: "+12,4M", isNegative: false)
                    DSMoneyBadge(value: "-3,1M", isNegative: true)
                }
                LoadingState(message: "Cargando datos…")
                ErrorState(message: "Algo salió mal")
            }
        }
    }

    @ViewBuilder
    private func section<Content: View>(
        _ title: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
            Text(title)
                .font(DSFont.h2)
                .foregroundStyle(DSColor.onSurface)
            content()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// Toggle switching the catalog between light and dark appearance. [FR5.2, BR1.1]
@available(iOS 15.0, macOS 12.0, *)
public struct ThemeToggle: View {
    @Binding private var isDark: Bool

    public init(isDark: Binding<Bool>) {
        self._isDark = isDark
    }

    public var body: some View {
        Toggle(isOn: $isDark) {
            Text("Modo oscuro").font(DSFont.body)
        }
        .accessibilityLabel("Modo oscuro")
        .accessibilityIdentifier("catalog-theme-toggle")
    }
}

/// Control cycling the catalog's Dynamic Type size to exercise scaling. [FR5, BR1.2]
@available(iOS 15.0, macOS 12.0, *)
public struct TextSizeControl: View {
    @Binding private var size: DynamicTypeSize

    public init(size: Binding<DynamicTypeSize>) {
        self._size = size
    }

    private let steps: [DynamicTypeSize] = [
        .small, .medium, .large, .xLarge, .xxLarge, .accessibility1
    ]

    public var body: some View {
        HStack(spacing: DSSpacingSwiftUI.sm) {
            Text("Tamaño de texto").font(DSFont.body)
            Spacer()
            Button("A-") { decrease() }
                .frame(minWidth: 44, minHeight: 44)
                .accessibilityIdentifier("catalog-text-size-decrease")
            Button("A+") { increase() }
                .frame(minWidth: 44, minHeight: 44)
                .accessibilityIdentifier("catalog-text-size-increase")
        }
    }

    private func increase() {
        guard let index = steps.firstIndex(of: size), index + 1 < steps.count else { return }
        size = steps[index + 1]
    }

    private func decrease() {
        guard let index = steps.firstIndex(of: size), index > 0 else { return }
        size = steps[index - 1]
    }
}

#endif // canImport(SwiftUI)
