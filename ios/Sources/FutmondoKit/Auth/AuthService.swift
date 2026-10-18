import Foundation

/// Owner of the session: the in-memory access token, the refresh-token
/// lifecycle, and the single coalesced refresh (AR1/AR3/AR4/AR5/AR8).
///
/// `AuthService` is an `actor`: the mutable `accessToken` and the refresh
/// orchestration are isolated, so the many async requests that read/mutate it
/// cannot race. The synchronous `accessTokenProvider` that `NetworkClient`
/// needs reads a Sendable snapshot (``TokenHolder``) that this actor updates on
/// every token change — it never enters the actor inline (AR8 / SEC-A2).
public actor AuthService {
    private let network: any NetworkClient & Sendable
    private let keychain: any KeychainStore & Sendable
    private let tokenHolder: TokenHolder
    private let flagStore: any LogoutFlagStore

    /// In-memory access token (AR2). Never persisted.
    private var accessToken: String?

    /// Coalescing handle for the in-flight refresh (AR4 / REL-A2). When set,
    /// concurrent callers await the same task instead of starting a new one.
    private var refreshInFlight: Task<String, Error>?

    public init(
        network: any NetworkClient & Sendable,
        keychain: any KeychainStore & Sendable,
        tokenHolder: TokenHolder,
        flagStore: any LogoutFlagStore = UserDefaultsLogoutFlagStore()
    ) {
        self.network = network
        self.keychain = keychain
        self.tokenHolder = tokenHolder
        self.flagStore = flagStore
    }

    // MARK: - Provider bridge (AR8 / SEC-A2)

    /// Synchronous, `Sendable` access-token provider for the `NetworkClient`.
    /// It reads the `TokenHolder` snapshot and never touches the actor, so it
    /// is safe to pass into `URLSessionNetworkClient(accessTokenProvider:)`.
    public nonisolated func accessTokenProvider() -> () -> String? {
        let holder = tokenHolder
        return { holder.get() }
    }

    // MARK: - Isolated reads

    /// Current in-memory access token (actor-isolated read).
    public func currentAccessToken() -> String? {
        accessToken
    }

    /// Whether a logout revocation is still pending because the network failed
    /// (AR5 / REL-A3). Read from the persisted boolean flag.
    public var pendingLogoutRevocation: Bool {
        flagStore.pendingLogoutRevocation()
    }

    // MARK: - AR1 — Login

    /// `POST /auth/login`. On 200: store the access token in memory and in the
    /// holder, persist the refresh token in the Keychain, and return a
    /// ``Session``. On 401/other 4xx: `.invalidCredentials`. Other network
    /// failures map to `.network(_)`.
    public func login(email: String, password: String) async -> Result<Session, AuthError> {
        let request = APIRequest(
            method: .post,
            path: "/auth/login",
            body: AnyEncodable(LoginRequestDTO(email: email, password: password))
        )

        let result: Result<LoginResponseDTO, NetworkError> = await network.send(request)
        switch result {
        case .success(let dto):
            setAccessToken(dto.accessToken)
            do {
                try keychain.saveRefreshToken(dto.refreshToken)
            } catch {
                // Could not persist the refresh token: do not claim a session
                // that cannot be restored. Clear the in-memory token too.
                setAccessToken(nil)
                return .failure(.unknown("keychain save failed"))
            }
            let user = UserMe(userId: dto.userId, email: dto.email)
            return .success(Session(accessToken: dto.accessToken, user: user))

        case .failure(.unauthorized), .failure(.clientError):
            return .failure(.invalidCredentials)

        case .failure(let error):
            return .failure(.network(error))
        }
    }

    // MARK: - AR4 — Refresh (single retry + coalescing)

    /// Mint a new access token from the stored refresh token. Concurrent
    /// callers share a single in-flight refresh task (AR4 / REL-A2): the first
    /// caller creates the task, the rest await it, and `refreshInFlight` is
    /// cleared once it resolves (success or failure). The new access token is
    /// stored in memory and in the holder.
    public func refresh() async -> Result<String, AuthError> {
        let task = currentOrNewRefreshTask()
        defer {
            // Clear the coalescing slot only if it still points at this task,
            // so a later refresh that already replaced it is not disturbed.
            // Runs on the actor's executor (this method is actor-isolated).
            if refreshInFlight == task {
                refreshInFlight = nil
            }
        }
        do {
            let token = try await task.value
            return .success(token)
        } catch let error as AuthError {
            return .failure(error)
        } catch {
            return .failure(.refreshFailed)
        }
    }

    /// Return the in-flight refresh task, or create and register a new one.
    private func currentOrNewRefreshTask() -> Task<String, Error> {
        if let inFlight = refreshInFlight {
            return inFlight
        }
        let task = Task<String, Error> { [self] in
            try await self.performRefresh()
        }
        refreshInFlight = task
        return task
    }

    /// Perform the actual refresh HTTP call exactly once. Reads the refresh
    /// token from the Keychain and sends it in the `X-Refresh-Token` header
    /// (D-01). Throws an ``AuthError`` on any failure.
    private func performRefresh() async throws -> String {
        guard let refreshToken = keychain.readRefreshToken() else {
            throw AuthError.refreshFailed
        }

        let request = APIRequest(
            method: .post,
            path: "/auth/refresh",
            headers: ["X-Refresh-Token": refreshToken]
        )

        let result: Result<RefreshResponseDTO, NetworkError> = await network.send(request)
        switch result {
        case .success(let dto):
            setAccessToken(dto.accessToken)
            return dto.accessToken
        case .failure(.unauthorized):
            // Revoked/expired refresh token.
            throw AuthError.refreshFailed
        case .failure(let error):
            throw AuthError.network(error)
        }
    }

    // MARK: - AR3 — Bootstrap (auto-login)

    /// Restore a session on startup (AR3 / REL-A1). Never hangs:
    /// - no refresh token in the Keychain → `.unauthenticated`;
    /// - refresh 200 → access token in memory → `.authenticated`;
    /// - 401/revoked → clear the Keychain → `.unauthenticated`;
    /// - transport/server/unexpected → preserve the Keychain → `.offlinePreserved`.
    public func bootstrap() async -> SessionState {
        guard let refreshToken = keychain.readRefreshToken() else {
            return .unauthenticated
        }

        let request = APIRequest(
            method: .post,
            path: "/auth/refresh",
            headers: ["X-Refresh-Token": refreshToken]
        )

        let result: Result<RefreshResponseDTO, NetworkError> = await network.send(request)
        switch result {
        case .success(let dto):
            setAccessToken(dto.accessToken)
            // F1 restores the session without a user-profile fetch (no data
            // screens yet, F2); surface a minimal user derived from the token
            // owner. The access token is what protected calls need now.
            let user = UserMe(userId: "", email: "")
            return .authenticated(Session(accessToken: dto.accessToken, user: user))

        case .failure(.unauthorized):
            // Revoked token: drop the stored credential so we ask for login.
            try? keychain.deleteRefreshToken()
            setAccessToken(nil)
            return .unauthenticated

        case .failure(.transport), .failure(.server), .failure(.unexpectedStatus):
            // Could be offline or a backend blip: keep the token, retry later.
            return .offlinePreserved

        case .failure:
            // forbidden / clientError / decoding / cancelled: treat as no
            // usable session but keep the token for a later attempt.
            return .offlinePreserved
        }
    }

    // MARK: - AR5 — Logout

    /// Revoke the session and tear down local state (AR5 / REL-A3). Teardown
    /// order is load-bearing: clear the holder FIRST (cuts off `Bearer`
    /// injection immediately), then the in-memory token, then delete the
    /// Keychain entry. If the network call fails, the local state is still
    /// cleared and `pendingLogoutRevocation` is set so a later startup retries.
    public func logout() async {
        let refreshToken = keychain.readRefreshToken()

        var headers: [String: String] = [:]
        if let refreshToken {
            headers["X-Refresh-Token"] = refreshToken
        }
        let request = APIRequest(method: .post, path: "/auth/logout", headers: headers)
        let result: Result<EmptyResponse, NetworkError> = await network.send(request)

        // Always tear down local state, regardless of the network outcome.
        // 1) Holder first — no in-flight request can attach the token after this.
        tokenHolder.set(nil)
        // 2) Actor-isolated token.
        accessToken = nil
        // 3) Keychain.
        try? keychain.deleteRefreshToken()

        switch result {
        case .success:
            setPendingLogoutRevocation(false)
        case .failure:
            // Network failed: mark the revocation as pending (boolean only;
            // the refresh token is NOT copied out of the Keychain — AR5/ADR-2).
            setPendingLogoutRevocation(true)
        }
    }

    // MARK: - Private helpers

    /// Update the in-memory access token AND its holder snapshot together, so
    /// the synchronous provider always sees the current value (SEC-A2).
    private func setAccessToken(_ token: String?) {
        accessToken = token
        tokenHolder.set(token)
    }

    private func setPendingLogoutRevocation(_ pending: Bool) {
        flagStore.setPendingLogoutRevocation(pending)
    }
}
