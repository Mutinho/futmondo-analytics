import XCTest
@testable import FutmondoKit

final class MarketWriteOutcomeTests: XCTestCase {
    private let fallback = "No se pudo registrar la operación."
    private let generic = "Error de red. Inténtalo de nuevo."

    private func outcome(
        _ result: Result<MarketWriteResponse, NetworkError>
    ) -> MarketWriteOutcome {
        MarketWriteOutcome.from(result: result, fallbackRejection: fallback, genericNetwork: generic)
    }

    // MARK: - 1. 2xx success=true → .accepted

    func testSuccessTrueIsAccepted() {
        XCTAssertEqual(outcome(.success(MarketWriteResponse(success: true))), .accepted)
    }

    // MARK: - 2. 2xx success=false with message → .rejected(message)

    func testSuccessFalseWithMessageIsRejected() {
        let response = MarketWriteResponse(success: false, message: "Puja ya superada")
        XCTAssertEqual(outcome(.success(response)), .rejected(message: "Puja ya superada"))
    }

    // MARK: - 3. 2xx success=false without message → .rejected(fallback)

    func testSuccessFalseWithoutMessageUsesFallback() {
        let response = MarketWriteResponse(success: false, message: nil, detail: nil)
        XCTAssertEqual(outcome(.success(response)), .rejected(message: fallback))
    }

    // MARK: - 4. 4xx (422/400) → .rejected(fallback)

    func testClientErrorIsRejected() {
        XCTAssertEqual(outcome(.failure(.clientError(422))), .rejected(message: fallback))
        XCTAssertEqual(outcome(.failure(.clientError(400))), .rejected(message: fallback))
    }

    // MARK: - 5. 401/403 → .rejected (business, not a network error)

    func testUnauthorizedAndForbiddenAreRejected() {
        XCTAssertEqual(outcome(.failure(.unauthorized)), .rejected(message: fallback))
        XCTAssertEqual(outcome(.failure(.forbidden)), .rejected(message: fallback))
    }

    // MARK: - 6. 5xx → .networkError

    func testServerErrorIsNetworkError() {
        XCTAssertEqual(outcome(.failure(.server(500))), .networkError)
        XCTAssertEqual(outcome(.failure(.server(503))), .networkError)
    }

    // MARK: - 7. transport / cancelled → .networkError

    func testTransportAndCancelledAreNetworkError() {
        XCTAssertEqual(outcome(.failure(.transport("offline"))), .networkError)
        XCTAssertEqual(outcome(.failure(.cancelled)), .networkError)
    }

    // MARK: - 8. No credential/message leak beyond backend prose

    func testRejectionCarriesOnlyBackendProseOrFallback() {
        // A rejection with a backend message carries exactly that text.
        let response = MarketWriteResponse(success: false, message: "Saldo insuficiente")
        guard case .rejected(let message) = outcome(.success(response)) else {
            return XCTFail("Expected .rejected")
        }
        XCTAssertEqual(message, "Saldo insuficiente")
        // A typed 4xx has no body to quote → the localized fallback, never a
        // token or raw error description.
        guard case .rejected(let fb) = outcome(.failure(.clientError(422))) else {
            return XCTFail("Expected .rejected")
        }
        XCTAssertEqual(fb, fallback)
    }
}
