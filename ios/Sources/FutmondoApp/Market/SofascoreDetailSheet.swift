import Foundation
import FutmondoKit

#if canImport(SwiftUI) && canImport(Observation)
import SwiftUI
import Observation

/// Sheet-local load state for the Sofascore detail (W7). Isolated from the
/// market list (FR8.2 / BR-UI-5): nothing here touches `MarketViewModel`.
public enum SofascoreDetailState: Equatable {
    case loading
    case data(SofascoreDetail)
    case empty
    case error
}

/// Isolated view model for one Sofascore detail sheet (V6 / FR8). Created fresh
/// per opened sheet so its state never bleeds into the list or another sheet.
@available(iOS 17.0, macOS 14.0, *)
@MainActor
@Observable
public final class SofascoreDetailViewModel {
    public private(set) var state: SofascoreDetailState = .loading

    private let service: any SofascoreService
    private let activeStore: any ActiveChampionshipStore

    public init(
        service: any SofascoreService,
        activeStore: any ActiveChampionshipStore
    ) {
        self.service = service
        self.activeStore = activeStore
    }

    /// Load the detail for `playerName`. Maps the typed outcome to the local
    /// state; a failure stays in this sheet (FR8.2).
    public func load(playerName: String) async {
        state = .loading
        let championshipId = activeStore.activeId ?? ""
        let outcome = await service.loadDetail(
            playerName: playerName,
            championshipId: championshipId
        )
        switch outcome {
        case .loaded(let detail): state = .data(detail)
        case .empty: state = .empty
        case .failed: state = .error
        }
    }
}

/// Sofascore detail sheet (V6 / W7), redesigned as an elegant, native,
/// full-screen stats page: it opens directly at `.large`, leads with a hero
/// (a tile-style wide player photo with the name + crest overlaid and the big
/// Sofascore rating on the right), then groups the stats into native `Grid`
/// Defensa · Disciplina) so most data is visible at a glance. The external
/// Sofascore link lives in the card's "…" menu, so it is intentionally NOT
/// repeated here. States loading / data / empty(404) / error stay local (FR8.2).
@available(iOS 17.0, macOS 14.0, *)
public struct SofascoreDetailSheet: View {
    private let playerName: String
    private let teamLogo: String?
    private let playerSlug: String?
    @State private var viewModel: SofascoreDetailViewModel
    @State private var appeared = false
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(
        playerName: String,
        sofascoreURL: String? = nil,
        teamLogo: String? = nil,
        playerSlug: String? = nil,
        viewModel: SofascoreDetailViewModel
    ) {
        self.playerName = playerName
        self.teamLogo = teamLogo
        self.playerSlug = playerSlug
        _viewModel = State(initialValue: viewModel)
    }

    public var body: some View {
        NavigationStack {
            ScrollView {
                content
                    .padding(DSSpacingSwiftUI.lg)
                    .opacity(appeared ? 1 : 0)
                    .offset(y: appeared || reduceMotion ? 0 : 12)
            }
            .background(DSColor.surface)
            .navigationTitle("Estadísticas")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Cerrar") { dismiss() }
                }
            }
        }
        .presentationDetents([.large])
        .presentationDragIndicator(.visible)
        .task {
            await viewModel.load(playerName: playerName)
            withAnimation(reduceMotion ? nil : .easeOut(duration: 0.35)) { appeared = true }
        }
        .accessibilityIdentifier("sofascore-detail-sheet")
    }

    @ViewBuilder
    private var content: some View {
        switch viewModel.state {
        case .loading:
            LoadingState(message: "Cargando estadísticas")
                .frame(maxWidth: .infinity, minHeight: 240)
        case .empty:
            emptyOrError(
                icon: "chart.bar.xaxis",
                title: "Sin datos de Sofascore",
                message: "Este jugador no tiene estadísticas disponibles."
            )
        case .error:
            emptyOrError(
                icon: "exclamationmark.triangle.fill",
                title: "No se pudieron cargar",
                message: "Inténtalo de nuevo en un momento.",
                isError: true
            )
        case .data(let detail):
            VStack(alignment: .leading, spacing: DSSpacingSwiftUI.lg) {
                heroCard(detail)
                statsSections(detail)
            }
        }
    }

    // MARK: - Hero (tile-style: wide player photo + name/crest overlay + big rating)

    private func heroCard(_ detail: SofascoreDetail) -> some View {
        let value = detail.rating
        let color = ratingColor(value)
        return ZStack(alignment: .bottomLeading) {
            heroImage
                .frame(maxWidth: .infinity)
                .frame(height: 150)
                .clipped()

            LinearGradient(
                colors: [.clear, .black.opacity(0.8)],
                startPoint: .center,
                endPoint: .bottom
            )

            // Big Sofascore rating, top-right.
            VStack(alignment: .trailing, spacing: 0) {
                Text(value.map { fmt1($0) } ?? "—")
                    .font(.system(size: 40, weight: .heavy, design: .rounded))
                    .foregroundStyle(.white)
                    .shadow(color: .black.opacity(0.6), radius: 3, y: 1)
                Text("SOFASCORE")
                    .font(.system(size: 9, weight: .heavy))
                    .tracking(1)
                    .foregroundStyle(.white.opacity(0.85))
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(color.opacity(0.85), in: RoundedRectangle(cornerRadius: 12))
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(.white.opacity(0.5), lineWidth: 1))
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topTrailing)
            .padding(DSSpacingSwiftUI.sm)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("Rating Sofascore \(value.map { fmt1($0) } ?? "sin dato")")

            // Name + team crest overlaid at the bottom.
            VStack(alignment: .leading, spacing: 4) {
                Text(playerName)
                    .font(.system(size: 26, weight: .heavy))
                    .foregroundStyle(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
                    .shadow(color: .black.opacity(0.7), radius: 3, y: 1)
                HStack(spacing: 6) {
                    TeamLogo(logo: teamLogo, team: detail.tournament ?? "", size: 22)
                    if let tournament = detail.tournament {
                        Text(tournament)
                            .font(.caption)
                            .foregroundStyle(.white.opacity(0.9))
                            .lineLimit(1)
                    }
                    if let season = detail.season {
                        Text("· \(season)")
                            .font(.caption)
                            .foregroundStyle(.white.opacity(0.7))
                            .lineLimit(1)
                    }
                }
            }
            .padding(DSSpacingSwiftUI.md)
        }
        .frame(height: 150)
        .frame(maxWidth: .infinity)
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(color.opacity(0.35), lineWidth: 1))
    }

    /// Wide semi-transparent player photo (same treatment as the market tile);
    /// a silhouette/colour fallback when there is no slug or the load fails.
    @ViewBuilder
    private var heroImage: some View {
        if let slug = playerSlug, let url = MarketImageURL.playerPhoto(slug: slug) {
            AsyncImage(url: url) { phase in
                switch phase {
                case .success(let image):
                    image.resizable().scaledToFill().opacity(0.6)
                default:
                    heroFallback
                }
            }
        } else {
            heroFallback
        }
    }

    private var heroFallback: some View {
        ZStack {
            DSColor.primary.opacity(0.25)
            Image(systemName: "person.fill")
                .font(.system(size: 56))
                .foregroundStyle(.white.opacity(0.4))
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Stats, grouped into native Grid sections

    @ViewBuilder
    private func statsSections(_ detail: SofascoreDetail) -> some View {
        let participacion: [(String, String, String)] = [
            ("sportscourt", "Partidos", detail.appearances.map(String.init) ?? "-"),
            ("figure.stand", "Titular", detail.matchesStarted.map(String.init) ?? "-"),
            ("percent", "% Titular", detail.starterPct.map { "\($0)%" } ?? "-"),
            ("clock", "Minutos", detail.minutesPlayed.map(String.init) ?? "-"),
        ]
        let ataque: [(String, String, String)] = [
            ("soccerball", "Goles", detail.goals.map(String.init) ?? "-"),
            ("hand.thumbsup", "Asistencias", detail.assists.map(String.init) ?? "-"),
            ("scope", "Tiros a puerta", detail.shotsOnTarget.map { fmt1($0) } ?? "-"),
            ("arrow.triangle.turn.up.right.diamond", "Regates", detail.successfulDribbles.map { fmt1($0) } ?? "-"),
            ("arrow.up.forward", "% Pases", detail.accuratePassesPct.map { fmt1($0) } ?? "-"),
        ]
        let defensa: [(String, String, String)] = [
            ("shield.lefthalf.filled", "Entradas", detail.tackles.map { fmt1($0) } ?? "-"),
            ("hand.raised", "Intercepciones", detail.interceptions.map { fmt1($0) } ?? "-"),
            ("lock.shield", "Porterías a cero", detail.cleanSheets.map(String.init) ?? "-"),
            ("hands.sparkles", "Paradas", detail.saves.map(String.init) ?? "-"),
        ]
        let disciplina: [(String, String, String)] = [
            ("rectangle.fill", "Amarillas", detail.yellowCards.map(String.init) ?? "-"),
            ("rectangle.portrait.fill", "Rojas", detail.redCards.map(String.init) ?? "-"),
        ]

        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.lg) {
            section("Participación", participacion)
            section("Ataque", ataque)
            section("Defensa", defensa)
            section("Disciplina", disciplina)
        }
    }

    private func section(_ title: String, _ rows: [(String, String, String)]) -> some View {
        VStack(alignment: .leading, spacing: DSSpacingSwiftUI.sm) {
            Text(title.uppercased())
                .font(.caption.weight(.heavy))
                .foregroundStyle(DSColor.primary)
                .accessibilityAddTraits(.isHeader)
            Grid(horizontalSpacing: DSSpacingSwiftUI.md, verticalSpacing: 0) {
                ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                    GridRow {
                        Image(systemName: row.0)
                            .font(.footnote)
                            .foregroundStyle(DSColor.onSurfaceVariant)
                            .frame(width: 22)
                            .gridColumnAlignment(.center)
                            .accessibilityHidden(true)
                        Text(row.1)
                            .font(DSFont.body)
                            .foregroundStyle(DSColor.onSurface)
                            .gridColumnAlignment(.leading)
                        Spacer(minLength: 0)
                        Text(row.2)
                            .font(DSFont.body.weight(.bold))
                            .foregroundStyle(row.2 == "-" ? DSColor.onSurfaceVariant : DSColor.onSurface)
                            .gridColumnAlignment(.trailing)
                    }
                    .padding(.vertical, 9)
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("\(row.1): \(row.2 == "-" ? "sin dato" : row.2)")
                    if index < rows.count - 1 {
                        Divider().overlay(DSColor.onSurface.opacity(0.08))
                    }
                }
            }
            .padding(.horizontal, DSSpacingSwiftUI.md)
            .padding(.vertical, 4)
            .background(DSColor.cardSurfaceDark.opacity(0.4), in: RoundedRectangle(cornerRadius: 14))
        }
    }

    private func emptyOrError(icon: String, title: String, message: String, isError: Bool = false) -> some View {
        VStack(spacing: DSSpacingSwiftUI.sm) {
            Image(systemName: icon)
                .font(.system(size: 40))
                .foregroundStyle(isError ? DSColor.moneyNegative : DSColor.onSurfaceVariant)
            Text(title)
                .font(DSFont.h3)
                .foregroundStyle(DSColor.onSurface)
            Text(message)
                .font(DSFont.body)
                .foregroundStyle(DSColor.onSurfaceVariant)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, minHeight: 240)
        .padding(DSSpacingSwiftUI.lg)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title). \(message)")
    }

    private func ratingColor(_ rating: Double?) -> Color {
        guard let rating else { return DSColor.onSurfaceVariant }
        if rating >= 7.0 { return DSColor.moneyPositive }
        if rating >= 6.0 { return DSColor.moneyPrize }
        return DSColor.moneyNegative
    }

    private func fmt1(_ value: Double) -> String { String(format: "%.1f", value) }
}

#endif // canImport(SwiftUI) && canImport(Observation)
