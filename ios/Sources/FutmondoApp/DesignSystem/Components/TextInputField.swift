import Foundation
import FutmondoKit

#if canImport(SwiftUI)
import SwiftUI

/// Text input reproducing the Angular `mat-form-field appearance="outline"`
/// with an optional prefix icon. Implements the states normal / focus / error
/// (BR2.2): an error shows a red border and error text; focus shows a primary
/// border; otherwise a neutral border. A secure field offers a visibility
/// toggle. [FR4.2, BR2.2]
@available(iOS 15.0, macOS 12.0, *)
public struct TextInputField: View {
    private let label: String
    @Binding private var text: String
    private let icon: Image?
    private let isSecure: Bool
    private let errorMessage: String?

    @FocusState private var isFocused: Bool
    @State private var isRevealed = false

    public init(
        label: String,
        text: Binding<String>,
        icon: Image? = nil,
        isSecure: Bool = false,
        errorMessage: String? = nil
    ) {
        self.label = label
        self._text = text
        self.icon = icon
        self.isSecure = isSecure
        self.errorMessage = errorMessage
    }

    private var hasError: Bool { errorMessage?.isEmpty == false }

    /// Border color per state: error > focus > neutral (BR2.2).
    private var borderColor: Color {
        if hasError { return DSColor.moneyNegative }
        if isFocused { return DSColor.primary }
        return DSColor.onSurfaceVariant
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.xs) {
            Text(label)
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurfaceVariant)

            HStack(spacing: DSSpacingSwiftUI.sm) {
                if let icon {
                    icon.foregroundStyle(DSColor.onSurfaceVariant)
                        .accessibilityHidden(true)
                }

                inputField

                if isSecure {
                    Button {
                        isRevealed.toggle()
                    } label: {
                        Image(systemName: isRevealed ? "eye.slash.fill" : "eye.fill")
                    }
                    .frame(minWidth: 44, minHeight: 44)
                    .foregroundStyle(DSColor.onSurfaceVariant)
                    .accessibilityLabel(isRevealed ? "Ocultar texto" : "Mostrar texto")
                    .accessibilityIdentifier("text-input-visibility-toggle")
                }
            }
            .padding(DSSpacingSwiftUI.sm)
            .overlay(
                RoundedRectangle(cornerRadius: 8).stroke(borderColor, lineWidth: 1)
            )

            if let errorMessage, !errorMessage.isEmpty {
                // Error conveyed by icon + text, not color alone (A7).
                HStack(spacing: DSSpacingSwiftUI.xs) {
                    Image(systemName: "exclamationmark.circle.fill")
                        .accessibilityHidden(true)
                    Text(errorMessage)
                        .font(DSFont.body)
                }
                .foregroundStyle(DSColor.moneyNegative)
                .accessibilityElement(children: .combine)
            }
        }
        .accessibilityIdentifier("text-input-\(label.lowercased())")
    }

    @ViewBuilder
    private var inputField: some View {
        Group {
            if isSecure && !isRevealed {
                SecureField(label, text: $text)
            } else {
                TextField(label, text: $text)
            }
        }
        .font(DSFont.body)
        .foregroundStyle(DSColor.onSurface)
        .focused($isFocused)
        .accessibilityLabel(label)
    }
}

#endif // canImport(SwiftUI)
