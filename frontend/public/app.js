/**
 * Main application JavaScript - Enhanced with interactive tooltips
 */

const API_URL = '/api/v1/matchdays';
const FINANCES_API_URL = '/api/v1/player-finances/';  // Add trailing slash to avoid 307 redirects
const USER_STATS_API_URL = '/api/v1/user-stats/';  // Add trailing slash to avoid 307 redirects
const CLAUSULABLE_PLAYERS_API_URL = '/api/v1/clausulable-players/';  // Add trailing slash to avoid 307 redirects
const ANALYTICS_BASE_URL = '/api/v1/analytics';
const ANALYTICS_ENDPOINTS = {
    trends: `${ANALYTICS_BASE_URL}/championship/trends`,
    customClassification: `${ANALYTICS_BASE_URL}/championship/custom-classification`,
    heatmap: `${ANALYTICS_BASE_URL}/championship/heatmap`,
    playerForm: `${ANALYTICS_BASE_URL}/players/form`,
    playerValue: `${ANALYTICS_BASE_URL}/players/value-trend`,
    userConsistency: `${ANALYTICS_BASE_URL}/users/consistency`,
    userMarketActivity: `${ANALYTICS_BASE_URL}/users/market-activity`,
    watchlist: `${ANALYTICS_BASE_URL}/market/watchlist`,
    clauseNetwork: `${ANALYTICS_BASE_URL}/clauses/network`,
    streaks: `${ANALYTICS_BASE_URL}/opportunities/streaks`,
    projections: `${ANALYTICS_BASE_URL}/projections/matchday`,
    balances: `${ANALYTICS_BASE_URL}/balances`
};
const HUMOR_API_URL = '/api/v1/humor/article';
const AUTH_BASE_URL = '/api/v1/auth';
const AUTH_ENDPOINTS = {
    login: `${AUTH_BASE_URL}/login`,
    session: `${AUTH_BASE_URL}/session`,
    logout: `${AUTH_BASE_URL}/logout`
};
const AUTH_STORAGE_KEY = 'futmondoAuth';
const HIDDEN_PREMIUM_TABS = new Set(['finances']);
const LOCKED_PREMIUM_TABS = new Set(['clausulable']);
const PREMIUM_TABS = new Set([...HIDDEN_PREMIUM_TABS, ...LOCKED_PREMIUM_TABS]);
const PREMIUM_ANALYTICS_SECTIONS = new Set(['players', 'users', 'market', 'opportunities', 'projections']);

// Chart.js global defaults
Chart.defaults.font.family = "'Segoe UI', Roboto, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.display = true;
Chart.defaults.plugins.legend.position = 'top';

let pointsChart = null;
let positionsChart = null;
let evolutionData = null;
let uniquePlayersChart = null;
let clausesChart = null;
let transactionsChart = null;
let analyticsMomentumChart = null;
let analyticsConsistencyChart = null;
let appInitialized = false;
let globalAccessMessageTimer = null;

function createDefaultAnalyticsLoadedState() {
    return {
        overview: false,
        custom: false,
        players: false,
        users: false,
        market: false,
        opportunities: false,
        projections: false
    };
}

const analyticsState = {
    loaded: createDefaultAnalyticsLoadedState(),
    caches: {}
};
let analyticsTeamMap = {};

function createDefaultHumorState() {
    return {
        initialized: false,
        matchdays: [],
        cache: new Map(),
        currentMatchday: null
    };
}

let humorState = createDefaultHumorState();

function createDefaultCustomClassificationState() {
    return {
        window: 5,
        pendingWindow: 5,
        excluded: new Set(),
        draftExcluded: new Set()
    };
}

let customClassificationState = createDefaultCustomClassificationState();
let customControlsInitialized = false;
function createDefaultAuthState() {
    return {
        isAuthenticated: false,
        username: null,
        role: 'guest',
        token: null,
        expiresAt: null
    };
}

let authState = createDefaultAuthState();
let authEventsBound = false;

function persistAuthState() {
    if (authState.isAuthenticated && authState.token) {
        const payload = {
            username: authState.username,
            role: authState.role,
            token: authState.token,
            expires_at: authState.expiresAt
        };
        try {
            localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(payload));
        } catch (error) {
            console.warn('No se pudo guardar la sesión localmente:', error);
        }
    } else {
        localStorage.removeItem(AUTH_STORAGE_KEY);
    }
}

function updateUserControls() {
    const loginForm = document.getElementById('login-form');
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');
    const badge = document.getElementById('user-badge');
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const loginError = document.getElementById('login-error');

    if (!badge || !logoutButton || !loginForm) {
        return;
    }

    if (!authState.isAuthenticated) {
        badge.textContent = 'Modo invitado';
        loginForm.style.display = 'flex';
        loginForm.reset();
        if (loginButton) {
            loginButton.style.display = 'inline-flex';
            loginButton.disabled = false;
        }
        logoutButton.style.display = 'none';
        if (usernameInput) {
            usernameInput.disabled = false;
            usernameInput.focus();
        }
        if (passwordInput) {
            passwordInput.disabled = false;
        }
        if (loginError) {
            loginError.textContent = '';
            loginError.style.display = 'none';
        }
        return;
    }

    const roleLabel = authState.role === 'premium' ? 'Premium' : 'Invitado';
    const usernameLabel = authState.username || 'Usuario';
    badge.textContent = `${usernameLabel} · ${roleLabel}`;

    loginForm.style.display = 'none';
    if (loginButton) {
        loginButton.style.display = 'none';
        loginButton.disabled = false;
    }
    if (usernameInput) {
        usernameInput.value = '';
        usernameInput.disabled = true;
    }
    if (passwordInput) {
        passwordInput.value = '';
        passwordInput.disabled = true;
    }
    if (loginError) {
        loginError.textContent = '';
        loginError.style.display = 'none';
    }

    logoutButton.style.display = 'inline-flex';
}

function resetCharts() {
    if (pointsChart) {
        pointsChart.destroy();
        pointsChart = null;
    }
    if (positionsChart) {
        positionsChart.destroy();
        positionsChart = null;
    }
    if (uniquePlayersChart) {
        uniquePlayersChart.destroy();
        uniquePlayersChart = null;
    }
    if (clausesChart) {
        clausesChart.destroy();
        clausesChart = null;
    }
    if (transactionsChart) {
        transactionsChart.destroy();
        transactionsChart = null;
    }
    if (analyticsMomentumChart) {
        analyticsMomentumChart.destroy();
        analyticsMomentumChart = null;
    }
    if (analyticsConsistencyChart) {
        analyticsConsistencyChart.destroy();
        analyticsConsistencyChart = null;
    }
}

function resetAnalyticsState() {
    analyticsState.loaded = createDefaultAnalyticsLoadedState();
    analyticsState.caches = {};
    analyticsTeamMap = {};
    customClassificationState = createDefaultCustomClassificationState();
    customControlsInitialized = false;
}

function hideAccessMessage(scope = 'global') {
    const elementId = scope === 'analytics' ? 'analytics-access-message' : 'global-access-message';
    const element = document.getElementById(elementId);
    if (scope === 'global' && globalAccessMessageTimer) {
        clearTimeout(globalAccessMessageTimer);
        globalAccessMessageTimer = null;
    }
    if (element) {
        element.textContent = '';
        element.style.display = 'none';
    }
}

function showAccessMessage(message, scope = 'global', timeout = 3500) {
    const elementId = scope === 'analytics' ? 'analytics-access-message' : 'global-access-message';
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.textContent = message;
    element.style.display = 'block';

    if (scope === 'global') {
        if (globalAccessMessageTimer) {
            clearTimeout(globalAccessMessageTimer);
        }
        globalAccessMessageTimer = setTimeout(() => {
            element.style.display = 'none';
            globalAccessMessageTimer = null;
        }, timeout);
    }
}

function resetAppState() {
    resetCharts();
    resetAnalyticsState();
    resetHumorTab();
    evolutionData = null;
    hideAccessMessage('global');
    hideAccessMessage('analytics');
    appInitialized = false;

    const content = document.getElementById('content');
    if (content) {
        content.style.display = 'none';
    }
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'block';
    }
}

function applyRoleRestrictions() {
    HIDDEN_PREMIUM_TABS.forEach(tabName => {
        const button = document.getElementById(`${tabName}-tab-button`);
        const tab = document.getElementById(`${tabName}-tab`);
        const shouldDisplay = authState.isAuthenticated;
        if (button) {
            button.style.display = shouldDisplay ? '' : 'none';
        }
        if (tab) {
            tab.style.display = shouldDisplay ? '' : 'none';
        }
    });

    LOCKED_PREMIUM_TABS.forEach(tabName => {
        const button = document.getElementById(`${tabName}-tab-button`);
        const tab = document.getElementById(`${tabName}-tab`);
        if (button) {
            button.style.display = '';
        }
        if (tab) {
            tab.style.display = '';
        }
        if (!authState.isAuthenticated) {
            lockPremiumTab(tabName);
        } else {
            unlockPremiumTab(tabName);
        }
    });

    if (!authState.isAuthenticated) {
        hideAccessMessage('analytics');
        showTab('evolution');
        return;
    }

    hideAccessMessage('analytics');
}

function setAuthState(partialState) {
    authState = {
        ...authState,
        ...partialState
    };
    persistAuthState();
    updateUserControls();
    applyRoleRestrictions();
}

function clearAuthState() {
    authState = createDefaultAuthState();
    persistAuthState();
    updateUserControls();
    applyRoleRestrictions();
}

function canAccessTab(tabName) {
    if (!authState.isAuthenticated && HIDDEN_PREMIUM_TABS.has(tabName)) {
        return false;
    }
    return true;
}

function canAccessAnalyticsSection(sectionName) {
    if (!authState.isAuthenticated) {
        return !PREMIUM_ANALYTICS_SECTIONS.has(sectionName);
    }
    if (authState.role === 'premium') {
        return true;
    }
    return !PREMIUM_ANALYTICS_SECTIONS.has(sectionName);
}

function lockAnalyticsSection(sectionName, message = 'Contenido reservado para clientes premium') {
    const baseId = `analytics-${sectionName}`;
    const loading = document.getElementById(`${baseId}-loading`);
    const error = document.getElementById(`${baseId}-error`);
    const content = document.getElementById(`${baseId}-content`);

    if (loading) {
        loading.style.display = 'none';
    }
    if (content) {
        content.style.display = 'none';
    }
    if (error) {
        error.textContent = message;
        error.style.display = 'block';
    } else {
        showAccessMessage(message, 'analytics', 4000);
    }
    analyticsState.loaded[sectionName] = false;
}

function lockPremiumTab(tabName, message = 'Contenido reservado para clientes premium') {
    if (tabName === 'clausulable') {
        const loading = document.getElementById('clausulable-loading');
        const error = document.getElementById('clausulable-error');
        const container = document.getElementById('clausulable-table-container');

        if (loading) {
            loading.style.display = 'none';
        }
        if (container) {
            container.style.display = 'none';
        }
        if (error) {
            error.textContent = message;
            error.style.display = 'block';
        } else {
            showAccessMessage(message);
        }
    }
}

function unlockPremiumTab(tabName) {
    if (tabName === 'clausulable') {
        const loading = document.getElementById('clausulable-loading');
        const error = document.getElementById('clausulable-error');
        const container = document.getElementById('clausulable-table-container');

        if (error) {
            error.style.display = 'none';
            error.textContent = '';
        }
        if (container) {
            container.style.display = 'none';
        }
        if (loading) {
            loading.style.display = 'none';
        }
    }
}

function showLoginView() {
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');

    if (loginButton) {
        loginButton.disabled = false;
    }
    if (logoutButton) {
        logoutButton.disabled = false;
    }
}

function hideLoginView() {
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');

    if (loginButton) {
        loginButton.disabled = false;
    }
    if (logoutButton) {
        logoutButton.disabled = false;
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

/**
 * Show content
 */
function showContent() {
    document.getElementById('content').style.display = 'block';
}

/**
 * Generate random colors for teams
 */
function generateColors(count) {
    const colors = [];
    // Use corporate colors: light green and metallic black with variations
    const baseColors = [
        '#90EE90', // Light green
        '#000000', // Metallic black
        '#32CD32', // Lime green
        '#2F4F2F', // Dark green
        '#228B22', // Forest green
        '#006400', // Dark green
        '#98FB98', // Pale green
        '#00FF00', // Green
    ];
    
    for (let i = 0; i < count; i++) {
        if (i < baseColors.length) {
            colors.push(baseColors[i]);
        } else {
            const hue = ((i - baseColors.length) * 137.508) % 360;
            colors.push(`hsl(${hue}, 70%, 50%)`);
        }
    }
    return colors;
}

/**
 * Load evolution data from API
 */
async function loadEvolutionData() {
    try {
        const response = await fetch(`${API_URL}/evolution`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (!data.success || !data.data) {
            throw new Error('Invalid data format');
        }
        
        return data.data;
    } catch (error) {
        console.error('Error loading data:', error);
        showError(`Error cargando datos: ${error.message}`);
        throw error;
    }
}

/**
 * Fetch data from analytics endpoints with optional query parameters
 */
async function fetchAnalyticsData(endpoint, params = {}) {
    try {
        const url = new URL(endpoint, window.location.origin);
        Object.entries(params).forEach(([key, value]) => {
            if (value === undefined || value === null) {
                return;
            }
            if (Array.isArray(value)) {
                url.searchParams.delete(key);
                value.forEach(item => {
                    if (item !== undefined && item !== null && item !== '') {
                        url.searchParams.append(key, item);
                    }
                });
            } else {
                url.searchParams.set(key, value);
            }
        });

        const response = await fetch(url.pathname + url.search);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Analytics fetch error:', error);
        throw error;
    }
}

/**
 * Create custom tooltip HTML for best player
 */
function createTooltipHTML(bestPlayer, matchday, teamName) {
    if (!bestPlayer || !bestPlayer.id) {
        console.warn('Invalid bestPlayer data:', bestPlayer);
        return null;
    }
    
    // Try to use static path first (best practice), fallback to API endpoint
    let photoUrl = `/api/v1/photos/${bestPlayer.id}?t=${Date.now()}`;
    if (bestPlayer.photo_local_path) {
        const filename = bestPlayer.photo_local_path.split('/').pop();
        photoUrl = `/static/photos/${filename}?t=${Date.now()}`;
    }
    
    const playerName = bestPlayer.name || 'Jugador desconocido';
    const points = bestPlayer.points || 0;
    const position = bestPlayer.position || 'N/A';
    
    // Create unique key for this tooltip to force update
    const tooltipKey = `${teamName}-${matchday}-${bestPlayer.id}-${Date.now()}`;
    
    return `
        <div class="custom-tooltip" data-key="${tooltipKey}" data-player-id="${bestPlayer.id}">
            <button class="close-tooltip" style="position: absolute; top: 5px; right: 5px; background: #ff6b6b; color: white; border: none; border-radius: 50%; width: 25px; height: 25px; cursor: pointer; font-size: 16px; line-height: 1;">×</button>
            <img src="${photoUrl}" alt="${playerName}" class="player-photo" 
                 onerror="this.onerror=null; this.src='/api/v1/photos/default?t=' + Date.now();"
                 loading="eager" style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px;">
            <div class="player-name">${playerName}</div>
            <div class="player-info">
                <div class="info-row">
                    <span class="info-label">Equipo:</span>
                    <span>${teamName}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Jornada:</span>
                    <span>J${matchday}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Puntos (jornada):</span>
                    <span style="color: #32CD32; font-weight: bold;">${points}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Puesto:</span>
                    <span style="color: #000000; font-weight: bold;">${position}º</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Create points evolution chart with interactive tooltips
 */
function createPointsChart(data) {
    const ctx = document.getElementById('pointsChart').getContext('2d');
    const colors = generateColors(data.teams.length);
    
    evolutionData = data; // Store for tooltip access
    
    const datasets = data.teams.map((team, index) => ({
        label: team.team_name,
        data: team.points_evolution,
        borderColor: colors[index],
        backgroundColor: colors[index] + '40',
        borderWidth: 3,
        fill: false,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 8,
        pointHoverBorderWidth: 3,
        pointBackgroundColor: colors[index],
        pointBorderColor: '#fff',
    }));
    
    if (pointsChart) {
        pointsChart.destroy();
    }
    
    // Create custom tooltip element (or reuse existing)
    let tooltipElement = document.querySelector('.custom-tooltip');
    if (!tooltipElement) {
        tooltipElement = document.createElement('div');
        tooltipElement.className = 'custom-tooltip';
        tooltipElement.style.display = 'none';
        tooltipElement.style.position = 'absolute';
        tooltipElement.style.pointerEvents = 'auto'; // Allow clicks
        tooltipElement.style.zIndex = '10000';
        document.body.appendChild(tooltipElement);
        
        // Add close button functionality
        tooltipElement.addEventListener('click', function(e) {
            if (e.target.classList.contains('close-tooltip')) {
                tooltipElement.style.display = 'none';
                tooltipElement.dataset.keepVisible = 'false';
            }
        });
    }
    
    pointsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.matchdays.map(md => `J${md}`),
            datasets: datasets
        },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                onClick: function(event, elements, chart) {
                    // Handle click on points
                    if (elements.length > 0) {
                        const element = elements[0];
                        const dataIndex = element.index;
                        const datasetIndex = element.datasetIndex;
                        const matchday = data.matchdays[dataIndex];
                        const team = data.teams[datasetIndex];
                        
                        // DEBUG: Log to verify correct data
                        console.log('Click event:', {
                            dataIndex,
                            datasetIndex,
                            matchday,
                            teamName: team.team_name,
                            teamId: team.team_id,
                            matchdaysLength: data.matchdays.length,
                            bestPlayersLength: team.best_players ? team.best_players.length : 0,
                            bestPlayerAtDataIndex: team.best_players && team.best_players.length > dataIndex ? team.best_players[dataIndex] : null,
                            allBestPlayers: team.best_players ? team.best_players.map((bp, idx) => ({
                                index: idx,
                                id: bp ? bp.id : null,
                                name: bp ? bp.name : null,
                                matchday: data.matchdays[idx]
                            })) : null
                        });
                        
                        // Get best player for this specific matchday and team
                        // CRITICAL: Use dataIndex to get the correct player for this matchday
                        // Ensure dataIndex is within bounds
                        if (!team.best_players || team.best_players.length <= dataIndex) {
                            console.error('Best players array is too short:', {
                                dataIndex,
                                bestPlayersLength: team.best_players ? team.best_players.length : 0,
                                matchdaysLength: data.matchdays.length
                            });
                            return;
                        }
                        
                        const bestPlayer = team.best_players[dataIndex];
                        
                        console.log('Click event details:', {
                            matchday,
                            dataIndex,
                            teamName: team.team_name,
                            bestPlayer: bestPlayer ? {
                                id: bestPlayer.id,
                                name: bestPlayer.name,
                                points: bestPlayer.points,
                                position: bestPlayer.position
                            } : null,
                            bestPlayersArrayLength: team.best_players ? team.best_players.length : 0,
                            fullBestPlayersArray: team.best_players ? JSON.stringify(team.best_players) : null
                        });
                        
                        // Validate bestPlayer exists and has valid ID
                        if (!bestPlayer) {
                            console.warn('No bestPlayer found for team:', team.team_name, 'matchday:', matchday, 'dataIndex:', dataIndex);
                            return;
                        }
                        
                        if (!bestPlayer.id || bestPlayer.id === '') {
                            console.warn('BestPlayer has no valid ID:', bestPlayer);
                            return;
                        }
                        
                        if (bestPlayer && bestPlayer.id) {
                            // Get or create tooltip element
                            let tooltipElement = document.querySelector('.custom-tooltip');
                            
                            if (!tooltipElement) {
                                // Create if doesn't exist
                                tooltipElement = document.createElement('div');
                                tooltipElement.className = 'custom-tooltip';
                                tooltipElement.style.position = 'absolute';
                                tooltipElement.style.pointerEvents = 'auto';
                                tooltipElement.style.zIndex = '10000';
                                document.body.appendChild(tooltipElement);
                                
                                // Add close button functionality
                                tooltipElement.addEventListener('click', function(e) {
                                    if (e.target.classList.contains('close-tooltip')) {
                                        tooltipElement.style.display = 'none';
                                        tooltipElement.dataset.keepVisible = 'false';
                                    }
                                });
                            }
                            
                            // CRITICAL: Clear previous content completely and update with NEW data
                            tooltipElement.innerHTML = '';
                            
                            // Create new tooltip content with current player data
                            const playerId = bestPlayer.id;
                            const playerName = bestPlayer.name || 'Jugador desconocido';
                            const points = bestPlayer.points || 0;
                            const position = bestPlayer.position || 'N/A';
                            // Try to use static path first (best practice), fallback to API endpoint
                            let photoUrl = `/api/v1/photos/${playerId}?t=${Date.now()}`;
                            if (bestPlayer.photo_local_path) {
                                const filename = bestPlayer.photo_local_path.split('/').pop();
                                photoUrl = `/static/photos/${filename}?t=${Date.now()}`;
                            }
                            
                            // Create unique key for this tooltip
                            const tooltipKey = `${team.team_id}-${matchday}-${playerId}-${Date.now()}`;
                            
                            tooltipElement.innerHTML = `
                                <div class="custom-tooltip" data-key="${tooltipKey}" data-player-id="${playerId}">
                                    <button class="close-tooltip" style="position: absolute; top: 5px; right: 5px; background: #ff6b6b; color: white; border: none; border-radius: 50%; width: 25px; height: 25px; cursor: pointer; font-size: 16px; line-height: 1;">×</button>
                                    <img src="${photoUrl}" alt="${playerName}" class="player-photo" 
                                         onerror="this.onerror=null; this.src='/api/v1/photos/default?t=' + Date.now();"
                                         loading="eager" style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px;">
                                    <div class="player-name">${playerName}</div>
                                    <div class="player-info">
                                        <div class="info-row">
                                            <span class="info-label">Equipo:</span>
                                            <span>${team.team_name}</span>
                                        </div>
                                        <div class="info-row">
                                            <span class="info-label">Jornada:</span>
                                            <span>J${matchday}</span>
                                        </div>
                                        <div class="info-row">
                                            <span class="info-label">Puntos (jornada):</span>
                                            <span style="color: #32CD32; font-weight: bold;">${points}</span>
                                        </div>
                                        <div class="info-row">
                                            <span class="info-label">Puesto:</span>
                                            <span style="color: #000000; font-weight: bold;">${position}º</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                            
                            // Update metadata
                            tooltipElement.dataset.keepVisible = 'true';
                            tooltipElement.dataset.teamId = team.team_id;
                            tooltipElement.dataset.matchday = matchday;
                            tooltipElement.dataset.playerId = playerId;
                            tooltipElement.style.display = 'block';
                            
                            // Position tooltip near clicked point
                            const point = element.element;
                            const canvasRect = chart.canvas.getBoundingClientRect();
                            const x = canvasRect.left + point.x;
                            const y = canvasRect.top + point.y;
                            
                            // Use requestAnimationFrame for better positioning and image loading
                            requestAnimationFrame(() => {
                                const tooltipHeight = tooltipElement.offsetHeight;
                                const tooltipWidth = tooltipElement.offsetWidth;
                                
                                let leftPos = x + 20;
                                let topPos = y - tooltipHeight / 2;
                                
                                // Adjust if tooltip goes off screen
                                if (leftPos + tooltipWidth > window.innerWidth) {
                                    leftPos = x - tooltipWidth - 20;
                                }
                                if (leftPos < 10) {
                                    leftPos = 10;
                                }
                                if (topPos < 10) {
                                    topPos = 10;
                                }
                                if (topPos + tooltipHeight > window.innerHeight) {
                                    topPos = window.innerHeight - tooltipHeight - 10;
                                }
                                
                                tooltipElement.style.left = leftPos + 'px';
                                tooltipElement.style.top = topPos + 'px';
                                
                                // Re-attach close button listener after innerHTML update
                                const closeBtn = tooltipElement.querySelector('.close-tooltip');
                                if (closeBtn) {
                                    closeBtn.addEventListener('click', function() {
                                        tooltipElement.style.display = 'none';
                                        tooltipElement.dataset.keepVisible = 'false';
                                    });
                                }
                                
                                // Force image reload - get fresh image element after innerHTML
                                const img = tooltipElement.querySelector('.player-photo');
                                if (img && playerId) {
                                    // Force reload with cache busting
                                    const newPhotoUrl = `/api/v1/photos/${playerId}?t=${Date.now()}`;
                                    console.log('Loading photo for player:', playerId, 'URL:', newPhotoUrl);
                                    img.src = newPhotoUrl;
                                    img.onerror = function() {
                                        console.warn('Failed to load photo for player:', playerId);
                                        this.src = `/api/v1/photos/default?t=${Date.now()}`;
                                    };
                                    img.onload = function() {
                                        console.log('Photo loaded successfully for player:', playerId);
                                    };
                                }
                            });
                        } else {
                            console.warn('No best player found for team:', team.team_name, 'matchday:', matchday, 'dataIndex:', dataIndex);
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 10,
                            font: {
                                size: 11
                            },
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        enabled: false, // Disable default tooltip
                        external: function(context) {
                        // Custom tooltip implementation
                        const tooltip = context.tooltip;
                        
                        // Hide tooltip on mouse out (only for hover, click is handled separately)
                        if (tooltip.opacity === 0) {
                            // Only hide if not clicked (we'll track click state)
                            const tooltipElement = document.querySelector('.custom-tooltip');
                            if (tooltipElement && !tooltipElement.dataset.keepVisible) {
                                tooltipElement.style.display = 'none';
                            }
                            return;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Jornada',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Puntos Acumulados',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    },
                    beginAtZero: true
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            onHover: (event, activeElements) => {
                event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
}

/**
 * Create positions evolution chart
 */
function createPositionsChart(data) {
    const ctx = document.getElementById('positionsChart').getContext('2d');
    const colors = generateColors(data.teams.length);
    
    const datasets = data.teams.map((team, index) => ({
        label: team.team_name,
        data: team.positions_evolution,
        borderColor: colors[index],
        backgroundColor: colors[index] + '40',
        borderWidth: 3,
        fill: false,
        tension: 0.3,
        pointRadius: 6,
        pointHoverRadius: 9,
        pointHoverBorderWidth: 3,
        pointBackgroundColor: colors[index],
        pointBorderColor: '#fff',
        pointStyle: 'circle'
    }));
    
    // Find max position for y-axis
    const maxPosition = Math.max(...data.teams.flatMap(t => t.positions_evolution));
    
    if (positionsChart) {
        positionsChart.destroy();
    }
    
    positionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.matchdays.map(md => `J${md}`),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: function(event, elements, chart) {
                // Handle click on points - same as points chart
                if (elements.length > 0) {
                    const element = elements[0];
                    const dataIndex = element.index;
                    const datasetIndex = element.datasetIndex;
                    const matchday = data.matchdays[dataIndex];
                    const team = data.teams[datasetIndex];
                    
                    // DEBUG: Log to verify correct data
                    console.log('Position chart click event:', {
                        dataIndex,
                        datasetIndex,
                        matchday,
                        teamName: team.team_name,
                        teamId: team.team_id,
                        bestPlayersLength: team.best_players ? team.best_players.length : 0,
                        bestPlayerAtDataIndex: team.best_players && team.best_players.length > dataIndex ? team.best_players[dataIndex] : null
                    });
                    
                    // Get best player for this specific matchday and team
                    // CRITICAL: Use dataIndex to get the correct player for this matchday
                    // Ensure dataIndex is within bounds
                    if (!team.best_players || team.best_players.length <= dataIndex) {
                        console.error('Best players array is too short:', {
                            dataIndex,
                            bestPlayersLength: team.best_players ? team.best_players.length : 0,
                            matchdaysLength: data.matchdays.length
                        });
                        return;
                    }
                    
                    const bestPlayer = team.best_players[dataIndex];
                    
                    // Validate bestPlayer exists and has valid ID
                    if (!bestPlayer) {
                        console.warn('No bestPlayer found for team:', team.team_name, 'matchday:', matchday, 'dataIndex:', dataIndex);
                        return;
                    }
                    
                    if (!bestPlayer.id || bestPlayer.id === '') {
                        console.warn('BestPlayer has no valid ID:', bestPlayer);
                        return;
                    }
                    
                    if (bestPlayer && bestPlayer.id) {
                        // Get or create tooltip element
                        let tooltipElement = document.querySelector('.custom-tooltip');
                        
                        if (!tooltipElement) {
                            // Create if doesn't exist
                            tooltipElement = document.createElement('div');
                            tooltipElement.className = 'custom-tooltip';
                            tooltipElement.style.position = 'absolute';
                            tooltipElement.style.pointerEvents = 'auto';
                            tooltipElement.style.zIndex = '10000';
                            document.body.appendChild(tooltipElement);
                            
                            // Add close button functionality
                            tooltipElement.addEventListener('click', function(e) {
                                if (e.target.classList.contains('close-tooltip')) {
                                    tooltipElement.style.display = 'none';
                                    tooltipElement.dataset.keepVisible = 'false';
                                }
                            });
                        }
                        
                        // CRITICAL: Clear previous content completely and update with NEW data
                        tooltipElement.innerHTML = '';
                        
                        // Create new tooltip content with current player data
                        const playerId = bestPlayer.id;
                        const playerName = bestPlayer.name || 'Jugador desconocido';
                        const points = bestPlayer.points || 0;
                        const position = bestPlayer.position || 'N/A';
                        // Try to use static path first (best practice), fallback to API endpoint
                        // Photo filename should be {playerId}.png or {playerId}.jpg
                        let photoUrl = `/api/v1/photos/${playerId}?t=${Date.now()}`;
                        
                        // If we have photo_local_path in the data, use it directly
                        if (bestPlayer.photo_local_path) {
                            const filename = bestPlayer.photo_local_path.split('/').pop();
                            photoUrl = `/static/photos/${filename}?t=${Date.now()}`;
                        }
                        
                        // Create unique key for this tooltip
                        const tooltipKey = `${team.team_id}-${matchday}-${playerId}-${Date.now()}`;
                        
                        tooltipElement.innerHTML = `
                            <div class="custom-tooltip" data-key="${tooltipKey}" data-player-id="${playerId}">
                                <button class="close-tooltip" style="position: absolute; top: 5px; right: 5px; background: #ff6b6b; color: white; border: none; border-radius: 50%; width: 25px; height: 25px; cursor: pointer; font-size: 16px; line-height: 1;">×</button>
                                <img src="${photoUrl}" alt="${playerName}" class="player-photo" 
                                     onerror="this.onerror=null; this.src='/api/v1/photos/default?t=' + Date.now();"
                                     loading="eager" style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px;">
                                <div class="player-name">${playerName}</div>
                                <div class="player-info">
                                    <div class="info-row">
                                        <span class="info-label">Equipo:</span>
                                        <span>${team.team_name}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Jornada:</span>
                                        <span>J${matchday}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Puntos (jornada):</span>
                                        <span style="color: #32CD32; font-weight: bold;">${points}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Puesto:</span>
                                        <span style="color: #000000; font-weight: bold;">${position}º</span>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        // Update metadata
                        tooltipElement.dataset.keepVisible = 'true';
                        tooltipElement.dataset.teamId = team.team_id;
                        tooltipElement.dataset.matchday = matchday;
                        tooltipElement.dataset.playerId = playerId;
                        tooltipElement.style.display = 'block';
                        
                        // Position tooltip near clicked point
                        const point = element.element;
                        const canvasRect = chart.canvas.getBoundingClientRect();
                        const x = canvasRect.left + point.x;
                        const y = canvasRect.top + point.y;
                        
                        // Use requestAnimationFrame for better positioning and image loading
                        requestAnimationFrame(() => {
                            const tooltipHeight = tooltipElement.offsetHeight;
                            const tooltipWidth = tooltipElement.offsetWidth;
                            
                            let leftPos = x + 20;
                            let topPos = y - tooltipHeight / 2;
                            
                            // Adjust if tooltip goes off screen
                            if (leftPos + tooltipWidth > window.innerWidth) {
                                leftPos = x - tooltipWidth - 20;
                            }
                            if (leftPos < 10) {
                                leftPos = 10;
                            }
                            if (topPos < 10) {
                                topPos = 10;
                            }
                            if (topPos + tooltipHeight > window.innerHeight) {
                                topPos = window.innerHeight - tooltipHeight - 10;
                            }
                            
                            tooltipElement.style.left = leftPos + 'px';
                            tooltipElement.style.top = topPos + 'px';
                            
                            // Re-attach close button listener after innerHTML update
                            const closeBtn = tooltipElement.querySelector('.close-tooltip');
                            if (closeBtn) {
                                closeBtn.addEventListener('click', function() {
                                    tooltipElement.style.display = 'none';
                                    tooltipElement.dataset.keepVisible = 'false';
                                });
                            }
                            
                            // Force image reload - get fresh image element after innerHTML
                            const img = tooltipElement.querySelector('.player-photo');
                            if (img && playerId) {
                                // Force reload with cache busting
                                const newPhotoUrl = `/api/v1/photos/${playerId}?t=${Date.now()}`;
                                img.src = newPhotoUrl;
                                img.onerror = function() {
                                    this.src = `/api/v1/photos/default?t=${Date.now()}`;
                                };
                            }
                        });
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10,
                        font: {
                            size: 11
                        },
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: Posición ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Jornada',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Posición',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    reverse: true, // Position 1 at top
                    min: 0.5,
                    max: maxPosition + 0.5,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return Math.round(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            onHover: (event, activeElements) => {
                event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
    
    // Custom plugin to add position labels on points
    const positionLabelsPlugin = {
        id: 'positionLabels',
        afterDatasetsDraw: function(chart) {
            const ctx = chart.ctx;
            ctx.save();
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            chart.data.datasets.forEach((dataset, datasetIndex) => {
                const meta = chart.getDatasetMeta(datasetIndex);
                dataset.data.forEach((value, index) => {
                    const point = meta.data[index];
                    if (point && !point.skip) {
                        const x = point.x;
                        const y = point.y;
                        
                        // Draw background circle
                        ctx.fillStyle = 'white';
                        ctx.strokeStyle = dataset.borderColor;
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.arc(x, y, 14, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.stroke();
                        
                        // Draw position number
                        ctx.fillStyle = '#333';
                        ctx.fillText(value.toString(), x, y);
                    }
                });
            });
            ctx.restore();
        }
    };
    
    Chart.register(positionLabelsPlugin);
    positionsChart.update();
}

/**
 * Display statistics
 */
function displayStats(data) {
    const statsDiv = document.getElementById('stats');
    statsDiv.innerHTML = '';
    
    const totalTeams = data.teams.length;
    const totalMatchdays = data.matchdays.length;
    const avgPoints = data.teams.reduce((sum, team) => {
        const lastPoints = team.points_evolution[team.points_evolution.length - 1];
        return sum + lastPoints;
    }, 0) / totalTeams;
    
    const stats = [
        { label: 'Equipos', value: totalTeams },
        { label: 'Jornadas', value: totalMatchdays },
        { label: 'Puntos promedio', value: Math.round(avgPoints) }
    ];
    
    stats.forEach(stat => {
        const statCard = document.createElement('div');
        statCard.className = 'stat-card';
        statCard.innerHTML = `
            <h3>${stat.label}</h3>
            <div class="value">${stat.value}</div>
        `;
        statsDiv.appendChild(statCard);
    });
}

function resetHumorTab() {
    humorState = createDefaultHumorState();

    const subtabs = document.getElementById('humor-subtabs');
    if (subtabs) {
        subtabs.innerHTML = '';
    }
    const loading = document.getElementById('humor-loading');
    if (loading) {
        loading.style.display = 'none';
    }
    const errorDiv = document.getElementById('humor-error');
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }
    const content = document.getElementById('humor-content');
    if (content) {
        content.style.display = 'none';
    }
    const body = document.getElementById('humor-article-body');
    if (body) {
        body.innerHTML = '';
    }
    const title = document.getElementById('humor-article-title');
    if (title) {
        title.textContent = '';
    }
    const meta = document.getElementById('humor-generated-at');
    if (meta) {
        meta.textContent = '';
        meta.style.display = 'none';
    }
    const summaryList = document.getElementById('humor-summary-list');
    if (summaryList) {
        summaryList.innerHTML = '';
    }
    const summaryCard = document.getElementById('humor-summary-card');
    if (summaryCard) {
        summaryCard.style.display = 'none';
    }
    const accessMessage = document.getElementById('humor-access-message');
    if (accessMessage) {
        accessMessage.textContent = '';
        accessMessage.style.display = 'none';
    }
    hideHumorEmpty();
}

function showHumorEmpty(message = 'Aún no hay crónicas disponibles.') {
    const emptyState = document.getElementById('humor-empty');
    if (emptyState) {
        emptyState.textContent = message;
        emptyState.style.display = 'block';
    }
    const content = document.getElementById('humor-content');
    if (content) {
        content.style.display = 'none';
    }
}

function hideHumorEmpty() {
    const emptyState = document.getElementById('humor-empty');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
}

function sanitizeMatchdays(matchdays) {
    if (!Array.isArray(matchdays)) {
        return [];
    }
    const unique = Array.from(new Set(matchdays.map(md => Number(md))));
    return unique.filter(Number.isInteger).sort((a, b) => b - a);
}

function ensureHumorTabInitialized() {
    if (!evolutionData || !Array.isArray(evolutionData.matchdays)) {
        return;
    }
    const matchdays = sanitizeMatchdays(evolutionData.matchdays);
    humorState.matchdays = matchdays;

    if (!humorState.initialized) {
        initializeHumorTab(matchdays);
    } else {
        updateHumorMatchdays(matchdays);
    }
}

function initializeHumorTab(matchdays) {
    const container = document.getElementById('humor-subtabs');
    if (!container) {
        return;
    }

    container.innerHTML = '';
    humorState.initialized = true;
    humorState.matchdays = Array.isArray(matchdays) ? [...matchdays] : [];

    if (humorState.matchdays.length === 0) {
        showHumorEmpty('Aún no hay crónicas disponibles.');
        return;
    }

    hideHumorEmpty();

    humorState.matchdays.forEach(matchday => {
        const button = document.createElement('button');
        button.className = 'humor-subtab-button';
        button.dataset.matchday = matchday;
        button.textContent = `J${matchday}`;
        button.addEventListener('click', () => selectHumorMatchday(matchday));
        container.appendChild(button);
    });

    const defaultMatchday = (humorState.currentMatchday && humorState.matchdays.includes(humorState.currentMatchday))
        ? humorState.currentMatchday
        : humorState.matchdays[0];

    selectHumorMatchday(defaultMatchday);
}

function updateHumorMatchdays(matchdays) {
    const sanitized = Array.isArray(matchdays) ? [...matchdays] : [];
    const current = humorState.matchdays || [];
    const sameLength = sanitized.length === current.length;
    const sameItems = sameLength && sanitized.every((value, index) => value === current[index]);
    if (sameItems) {
        return;
    }
    humorState.initialized = false;
    initializeHumorTab(sanitized);
}

function selectHumorMatchday(matchday) {
    const numericMatchday = Number(matchday);
    if (!Number.isInteger(numericMatchday)) {
        return;
    }

    humorState.currentMatchday = numericMatchday;

    document.querySelectorAll('.humor-subtab-button').forEach(button => {
        const buttonMatchday = Number(button.dataset.matchday);
        button.classList.toggle('active', buttonMatchday === numericMatchday);
    });

    loadHumorArticle(numericMatchday);
}

async function loadHumorArticle(matchday) {
    const accessMessage = document.getElementById('humor-access-message');
    const loading = document.getElementById('humor-loading');
    const errorDiv = document.getElementById('humor-error');
    const content = document.getElementById('humor-content');

    if (accessMessage) {
        accessMessage.textContent = '';
        accessMessage.style.display = 'none';
    }
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }
    hideHumorEmpty();
    if (content) {
        content.style.display = 'none';
    }
    if (loading) {
        loading.style.display = 'block';
    }

    if (humorState.cache.has(matchday)) {
        if (loading) {
            loading.style.display = 'none';
        }
        renderHumorArticle(matchday, humorState.cache.get(matchday));
        return;
    }

    try {
        const response = await fetch(`${HUMOR_API_URL}?matchday=${encodeURIComponent(matchday)}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const payload = await response.json();
        if (!payload || payload.success !== true || !payload.data) {
            throw new Error('Formato de datos inválido');
        }

        humorState.cache.set(matchday, payload.data);
        if (loading) {
            loading.style.display = 'none';
        }
        renderHumorArticle(matchday, payload.data);
    } catch (error) {
        console.error('Error cargando crónica:', error);
        if (loading) {
            loading.style.display = 'none';
        }
        if (content) {
            content.style.display = 'none';
        }
        if (errorDiv) {
            const baseMessage = `No se pudo cargar la crónica de la jornada ${matchday}.`;
            const detail = error && error.message ? ` ${error.message}` : '';
            errorDiv.textContent = `${baseMessage}${detail}`.trim();
            errorDiv.style.display = 'block';
        } else {
            showAccessMessage(`No se pudo cargar la crónica de la jornada ${matchday}.`, 'global', 5000);
        }
    }
}

function renderHumorArticle(matchday, articleData) {
    const loading = document.getElementById('humor-loading');
    if (loading) {
        loading.style.display = 'none';
    }

    const errorDiv = document.getElementById('humor-error');
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }

    const content = document.getElementById('humor-content');
    if (content) {
        content.style.display = 'block';
    }

    const title = document.getElementById('humor-article-title');
    if (title) {
        title.textContent = `Crónica jornada ${matchday}`;
    }

    const meta = document.getElementById('humor-generated-at');
    if (meta) {
        if (articleData && articleData.generated_at) {
            const generatedDate = new Date(articleData.generated_at);
            if (!Number.isNaN(generatedDate.valueOf())) {
                meta.textContent = `Generada el ${generatedDate.toLocaleString('es-ES')}`;
                meta.style.display = 'block';
            } else {
                meta.textContent = '';
                meta.style.display = 'none';
            }
        } else {
            meta.textContent = '';
            meta.style.display = 'none';
        }
    }

    const body = document.getElementById('humor-article-body');
    if (body) {
        body.innerHTML = '';
        const articleText = articleData && articleData.article ? String(articleData.article).trim() : '';
        let paragraphs = articleText.split(/\n{2,}/).map(segment => segment.trim()).filter(Boolean);
        if (paragraphs.length === 0 && articleText) {
            paragraphs = [articleText];
        }

        if (paragraphs.length === 0) {
            const placeholder = document.createElement('p');
            placeholder.textContent = 'Todavía no hay contenido para esta jornada.';
            body.appendChild(placeholder);
        } else {
            paragraphs.forEach(segment => {
                const paragraph = document.createElement('p');
                paragraph.textContent = segment.replace(/\n+/g, ' ');
                body.appendChild(paragraph);
            });
        }
    }

    const summaryCard = document.getElementById('humor-summary-card');
    const summaryList = document.getElementById('humor-summary-list');
    if (summaryList) {
        summaryList.innerHTML = '';
    }

    const summary = Array.isArray(articleData?.summary) ? articleData.summary : [];
    if (summaryCard && summaryList && summary.length > 0) {
        summaryCard.style.display = 'block';
        summary.forEach(item => {
            const li = document.createElement('li');
            li.textContent = String(item).replace(/^[•\-\s]+/, '').trim();
            summaryList.appendChild(li);
        });
    } else if (summaryCard) {
        summaryCard.style.display = 'none';
    }
}

/**
 * Initialize application
 */
async function init() {
    try {
        const data = await loadEvolutionData();
        evolutionData = data;
        
        displayStats(data);
        createPointsChart(data);
        createPositionsChart(data);
        ensureHumorTabInitialized();
        
        hideLoading();
        showContent();
    } catch (error) {
        hideLoading();
        console.error('Initialization error:', error);
    }
}

/**
 * Show specific tab
 */
function showTab(tabName) {
    if (!canAccessTab(tabName)) {
        showAccessMessage('Contenido reservado para clientes premium');
        return;
    }

    hideAccessMessage('global');

    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    const tabElement = document.getElementById(`${tabName}-tab`);
    if (tabElement) {
        tabElement.classList.add('active');
    }

    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => {
        const btnText = btn.textContent.toLowerCase();
        if ((tabName === 'budget' && btnText.includes('presupuesto')) ||
            (tabName === 'evolution' && btnText.includes('evolución')) ||
            (tabName === 'finances' && btnText.includes('finanzas')) ||
            (tabName === 'stats' && btnText.includes('estadísticas')) ||
            (tabName === 'clausulable' && btnText.includes('clausulables')) ||
            (tabName === 'humor' && btnText.includes('crónicas')) ||
            (tabName === 'analytics' && btnText.includes('analytics'))) {
            btn.classList.add('active');
        }
    });

    if (tabName === 'budget') {
        loadBudgetTab();
    } else if (tabName === 'finances') {
        loadFinancesData();
    } else if (tabName === 'stats') {
        loadUserStatsData();
    } else if (tabName === 'clausulable') {
        loadClausulablePlayersData();
    } else if (tabName === 'humor') {
        ensureHumorTabInitialized();
        if (humorState.initialized && humorState.matchdays.length > 0) {
            const targetMatchday = humorState.currentMatchday && humorState.matchdays.includes(humorState.currentMatchday)
                ? humorState.currentMatchday
                : humorState.matchdays[0];
            selectHumorMatchday(targetMatchday);
        } else {
            showHumorEmpty('Aún no hay crónicas disponibles.');
        }
    } else if (tabName === 'analytics') {
        showAnalyticsSection('overview');
    }
}

/**
 * Format money value
 */
function formatMoney(value) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
        return '-';
    }
    return Number(value).toLocaleString('es-ES', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

/**
 * Load finances data from API
 */
async function loadFinancesData() {
    if (!canAccessTab('finances')) {
        showAccessMessage('Contenido reservado para clientes premium');
        return;
    }

    const loadingDiv = document.getElementById('finances-loading');
    const errorDiv = document.getElementById('finances-error');
    const tableContainer = document.getElementById('finances-table-container');
    const tableBody = document.getElementById('finances-table-body');
    
    // Show loading
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    tableContainer.style.display = 'none';
    
    try {
        const response = await fetch(FINANCES_API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (!data.success || !data.users) {
            throw new Error('Invalid data format');
        }
        
        // Clear table
        tableBody.innerHTML = '';
        
        // Populate table
        data.users.forEach(user => {
            const row = document.createElement('tr');
            
            const teamNameCell = document.createElement('td');
            teamNameCell.className = 'player-name';
            teamNameCell.textContent = user.team_name || 'Unknown';
            
            const usernameCell = document.createElement('td');
            usernameCell.textContent = user.username || user.team_name || '-';
            
            const pointsCell = document.createElement('td');
            pointsCell.textContent = user.total_points || 0;
            
            const pointsMoneyCell = document.createElement('td');
            pointsMoneyCell.className = 'money-positive';
            pointsMoneyCell.textContent = formatMoney(user.points_money || 0);
            
            const transactionCell = document.createElement('td');
            const transactionProfit = user.transaction_profit || 0;
            transactionCell.className = transactionProfit >= 0 ? 'money-positive' : 'money-negative';
            transactionCell.textContent = formatMoney(transactionProfit);
            
            const idealTeamCountCell = document.createElement('td');
            idealTeamCountCell.textContent = user.ideal_team_count || 0;
            
            const idealTeamCell = document.createElement('td');
            idealTeamCell.className = user.ideal_team_bonus > 0 ? 'money-positive' : '';
            idealTeamCell.textContent = formatMoney(user.ideal_team_bonus || 0);
            
            const mvpCountCell = document.createElement('td');
            mvpCountCell.textContent = user.mvp_count || 0;
            
            const mvpCell = document.createElement('td');
            mvpCell.className = user.mvp_bonus > 0 ? 'money-positive' : '';
            mvpCell.textContent = formatMoney(user.mvp_bonus || 0);
            
            const totalBonusCell = document.createElement('td');
            totalBonusCell.className = user.total_bonus > 0 ? 'money-positive' : '';
            totalBonusCell.textContent = formatMoney(user.total_bonus || 0);
            
            const totalCell = document.createElement('td');
            totalCell.className = 'money-total';
            totalCell.textContent = formatMoney(user.total_money || 0);
            
            row.appendChild(teamNameCell);
            row.appendChild(usernameCell);
            row.appendChild(pointsCell);
            row.appendChild(pointsMoneyCell);
            row.appendChild(transactionCell);
            row.appendChild(idealTeamCountCell);
            row.appendChild(idealTeamCell);
            row.appendChild(mvpCountCell);
            row.appendChild(mvpCell);
            row.appendChild(totalBonusCell);
            row.appendChild(totalCell);
            
            tableBody.appendChild(row);
        });
        
        // Hide loading, show table
        loadingDiv.style.display = 'none';
        tableContainer.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading finances data:', error);
        loadingDiv.style.display = 'none';
        errorDiv.textContent = `Error cargando datos financieros: ${error.message}`;
        errorDiv.style.display = 'block';
    }
}

/**
 * Load user statistics data and create charts
 */
async function loadUserStatsData() {
    const loadingDiv = document.getElementById('stats-loading');
    const errorDiv = document.getElementById('stats-error');
    const chartsContainer = document.getElementById('stats-charts-container');
    
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    chartsContainer.style.display = 'none';
    
    try {
        const response = await fetch(USER_STATS_API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('User stats data received:', data);
        
        if (!data.success || !data.users) {
            console.error('Invalid data format:', data);
            throw new Error('Invalid data format');
        }
        
        if (data.users.length === 0) {
            console.warn('No users found in stats data');
            loadingDiv.style.display = 'none';
            errorDiv.textContent = 'No hay datos de usuarios disponibles';
            errorDiv.style.display = 'block';
            return;
        }
        
        // Sort users by unique players count (descending), then by clauses paid (descending)
        const users = data.users.sort((a, b) => {
            // First by unique players count
            if (b.unique_players_count !== a.unique_players_count) {
                return b.unique_players_count - a.unique_players_count;
            }
            // Then by clauses paid
            if (b.clauses_paid !== a.clauses_paid) {
                return b.clauses_paid - a.clauses_paid;
            }
            // Finally by name
            const nameA = (a.team_name || a.username || '').toLowerCase();
            const nameB = (b.team_name || b.username || '').toLowerCase();
            return nameA.localeCompare(nameB);
        });
        
        console.log(`Processing ${users.length} users for charts`);
        
        // Filter out "Unknown" users from transactions chart (they are the Market)
        const usersForTransactions = users.filter(u => {
            const name = (u.team_name || u.username || '').toLowerCase();
            return name !== 'unknown' && name !== 'mercado';
        });
        
        // Sort transactions by transaction_count (descending)
        const sortedUsersForTransactions = usersForTransactions.sort((a, b) => {
            return (b.transaction_count || 0) - (a.transaction_count || 0);
        });
        
        // Extract data for charts
        const labels = users.map(u => u.team_name || u.username || 'Unknown');
        const uniquePlayers = users.map(u => u.unique_players_count || 0);
        const clausesPaid = users.map(u => u.clauses_paid || 0);
        const clausesReceived = users.map(u => u.clauses_received || 0);
        const transactionLabels = sortedUsersForTransactions.map(u => u.team_name || u.username || 'Unknown');
        const transactions = sortedUsersForTransactions.map(u => u.transaction_count || 0);
        
        console.log('Chart data:', {
            labels: labels.length,
            uniquePlayers: uniquePlayers.length,
            clausesPaid: clausesPaid.length,
            clausesReceived: clausesReceived.length,
            transactions: transactions.length
        });
        
        // Create charts
        try {
            createUniquePlayersChart(labels, uniquePlayers);
            createClausesChart(labels, clausesPaid, clausesReceived);
            createTransactionsChart(transactionLabels, transactions);
            console.log('All charts created successfully');
        } catch (chartError) {
            console.error('Error creating charts:', chartError);
            throw chartError;
        }
        
        loadingDiv.style.display = 'none';
        chartsContainer.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading user stats:', error);
        loadingDiv.style.display = 'none';
        errorDiv.textContent = `Error al cargar estadísticas: ${error.message}`;
        errorDiv.style.display = 'block';
    }
}

/**
 * Create chart for unique players
 */
function createUniquePlayersChart(labels, data) {
    const ctx = document.getElementById('uniquePlayersChart');
    if (!ctx) {
        console.error('Canvas element uniquePlayersChart not found');
        return;
    }
    
    if (uniquePlayersChart) {
        uniquePlayersChart.destroy();
    }
    
    uniquePlayersChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jugadores Únicos Alineados',
                data: data,
                backgroundColor: '#90EE90',
                borderColor: '#000000',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Create chart for clauses (paid and received grouped)
 */
function createClausesChart(labels, clausesPaid, clausesReceived) {
    const ctx = document.getElementById('clausesChart');
    if (!ctx) {
        console.error('Canvas element clausesChart not found');
        return;
    }
    
    if (clausesChart) {
        clausesChart.destroy();
    }
    
    clausesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Cláusulas Pagadas',
                    data: clausesPaid,
                    backgroundColor: '#32CD32',  // Verde claro
                    borderColor: '#000000',
                    borderWidth: 2
                },
                {
                    label: 'Cláusulas Recibidas',
                    data: clausesReceived,
                    backgroundColor: '#DC143C',  // Rojo
                    borderColor: '#000000',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Create chart for transactions
 */
function createTransactionsChart(labels, data) {
    const ctx = document.getElementById('transactionsChart');
    if (!ctx) {
        console.error('Canvas element transactionsChart not found');
        return;
    }
    
    if (transactionsChart) {
        transactionsChart.destroy();
    }
    
    transactionsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Número de Operaciones',
                data: data,
                backgroundColor: '#32CD32',  // Verde
                borderColor: '#000000',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Load clausulable players data
 */
async function loadClausulablePlayersData() {
    const loadingDiv = document.getElementById('clausulable-loading');
    const errorDiv = document.getElementById('clausulable-error');
    const tableContainer = document.getElementById('clausulable-table-container');
    const tableBody = document.getElementById('clausulable-table-body');

    if (!authState.isAuthenticated) {
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
        if (tableContainer) {
            tableContainer.style.display = 'none';
        }
        if (errorDiv) {
            errorDiv.textContent = 'Contenido reservado para clientes premium';
            errorDiv.style.display = 'block';
        } else {
            showAccessMessage('Contenido reservado para clientes premium');
        }
        return;
    }

    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
    
    loadingDiv.style.display = 'block';
    tableContainer.style.display = 'none';
    
    try {
        const response = await fetch(CLAUSULABLE_PLAYERS_API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('Clausulable players data received:', data);
        
        if (!data.success || !data.players) {
            console.error('Invalid data format:', data);
            throw new Error('Invalid data format');
        }
        
        if (data.players.length === 0) {
            loadingDiv.style.display = 'none';
            errorDiv.textContent = 'No hay jugadores clausulables disponibles';
            errorDiv.style.display = 'block';
            return;
        }
        
        // Store all players data for sorting
        window.clausulablePlayersData = data.players;
        
        // Show top 20 by default (sorted by final_score descending)
        // Reset sort state
        clausulableSortColumn = 'final_score';
        clausulableSortDirection = 'desc';
        displayClausulablePlayers(data.players);
        
        // Setup sorting
        setupClausulableTableSorting();
        
        loadingDiv.style.display = 'none';
        tableContainer.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading clausulable players:', error);
        loadingDiv.style.display = 'none';
        errorDiv.textContent = `Error al cargar jugadores clausulables: ${error.message}`;
        errorDiv.style.display = 'block';
    }
}

/**
 * Display clausulable players in table (shows top 20)
 */
function displayClausulablePlayers(players) {
    const tableBody = document.getElementById('clausulable-table-body');
    tableBody.innerHTML = '';
    
    // Show only top 20
    const topPlayers = players.slice(0, 20);
    
    topPlayers.forEach((player, index) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${player.player_name || 'Unknown'}</td>
            <td>${player.owner_name || 'Free Agent'}</td>
            <td>${player.metric1_score.toFixed(4)}</td>
            <td>${player.metric2_score.toFixed(4)}</td>
            <td>${player.metric3_score.toFixed(4)}</td>
            <td><strong>${player.final_score.toFixed(4)}</strong></td>
            <td>${player.clause_price.toLocaleString('es-ES')} €</td>
            <td>${player.suggested_clause.toLocaleString('es-ES')} €</td>
            <td>${player.average_last_five.toFixed(2)}</td>
            <td>${player.average_overall.toFixed(2)}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Sort clausulable players table
 */
let clausulableSortColumn = 'final_score';
let clausulableSortDirection = 'desc';

function sortClausulablePlayers(column) {
    if (!window.clausulablePlayersData || window.clausulablePlayersData.length === 0) {
        return;
    }
    
    // Toggle sort direction if clicking same column
    if (clausulableSortColumn === column) {
        clausulableSortDirection = clausulableSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        clausulableSortColumn = column;
        clausulableSortDirection = 'desc';
    }
    
    // Sort players
    const sorted = [...window.clausulablePlayersData].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle string comparison
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        if (clausulableSortDirection === 'asc') {
            return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
        } else {
            return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
        }
    });
    
    // Update table header indicators
    document.querySelectorAll('#clausulable-table th.sortable').forEach(th => {
        th.classList.remove('asc', 'desc');
        if (th.dataset.sort === column) {
            th.classList.add(clausulableSortDirection);
        }
    });
    
    // Display sorted players (top 20)
    displayClausulablePlayers(sorted);
}

/**
 * Setup sortable table headers for clausulable players
 */
function setupClausulableTableSorting() {
    document.querySelectorAll('#clausulable-table th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;
            if (column) {
                sortClausulablePlayers(column);
            }
        });
    });
}

function populateTable(tableId, headers, rows) {
    const table = document.getElementById(tableId);
    if (!table) {
        return;
    }
    const thead = table.querySelector('thead') || table.createTHead();
    const tbody = table.querySelector('tbody') || table.createTBody();

    thead.innerHTML = '';
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    tbody.innerHTML = '';
    rows.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach(cell => {
            const td = document.createElement('td');
            if (cell && typeof cell === 'object' && !Array.isArray(cell)) {
                if (cell.html) {
                    td.innerHTML = cell.html;
                } else if (cell.text !== undefined && cell.text !== null) {
                    td.textContent = cell.text;
                } else {
                    td.textContent = '';
                }
                if (cell.className) {
                    td.className = cell.className;
                }
                if (cell.style) {
                    Object.entries(cell.style).forEach(([prop, value]) => {
                        td.style[prop] = value;
                    });
                }
            } else {
                td.textContent = cell ?? '';
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function trendBadge(value, decimals = 2) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
        return { text: '-' };
    }
    const formatted = formatNumber(Math.abs(value), decimals);
    if (value > 0) {
        return { html: `<span class="analytics-pill badge-easy">▲ ${formatted}</span>` };
    }
    if (value < 0) {
        return { html: `<span class="analytics-pill badge-hard">▼ ${formatted}</span>` };
    }
    return { html: `<span class="analytics-pill badge-medium">● ${formatted}</span>` };
}

function showAnalyticsSection(sectionName) {
    const targetSectionId = `analytics-${sectionName}-section`;

    document.querySelectorAll('.analytics-tab-button').forEach(button => {
        const target = button.dataset.section;
        button.classList.toggle('active', target === sectionName);
    });

    document.querySelectorAll('.analytics-section').forEach(section => {
        section.classList.toggle('active', section.id === targetSectionId);
    });

    if (!canAccessAnalyticsSection(sectionName)) {
        lockAnalyticsSection(sectionName);
        showAccessMessage('Contenido reservado para clientes premium', 'analytics');
        return;
    }

    hideAccessMessage('analytics');

    if (!analyticsState.loaded[sectionName]) {
        if (sectionName === 'overview') {
            loadAnalyticsOverview();
        } else if (sectionName === 'custom') {
            loadAnalyticsCustom();
        } else if (sectionName === 'players') {
            loadAnalyticsPlayers();
        } else if (sectionName === 'users') {
            loadAnalyticsUsers();
        } else if (sectionName === 'market') {
            loadAnalyticsMarket();
        } else if (sectionName === 'opportunities') {
            loadAnalyticsOpportunities();
        } else if (sectionName === 'projections') {
            loadAnalyticsProjections();
        }
    }
}

async function loadAnalyticsOverview() {
    const loading = document.getElementById('analytics-overview-loading');
    const error = document.getElementById('analytics-overview-error');
    const content = document.getElementById('analytics-overview-content');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    try {
        const [trends, heatmap] = await Promise.all([
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.trends, { window: 5 }),
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.heatmap)
        ]);

        analyticsState.caches.trends = trends;
        analyticsState.caches.heatmap = heatmap;
        analyticsTeamMap = {};
        if (trends && Array.isArray(trends.teams)) {
            trends.teams.forEach(team => {
                analyticsTeamMap[team.team_id] = team.team_name;
            });
        }

        renderMomentumChart(trends);
        renderTrendsTable(trends);
        renderHeatmapTable(heatmap, trends);

        analyticsState.loaded.overview = true;
        loading.style.display = 'none';
        content.style.display = 'block';
    } catch (err) {
        console.error('Overview analytics error:', err);
        loading.style.display = 'none';
        error.textContent = `No se pudo cargar la visión general: ${err.message}`;
        error.style.display = 'block';
    }
}

function getCurrentCustomData() {
    return analyticsState.caches.custom || {
        available_matchdays: [],
        included_matchdays: [],
        excluded_matchdays: [],
        classification: [],
        window: customClassificationState.window
    };
}

function clampWindow(value) {
    const parsed = Number(value);
    if (Number.isNaN(parsed) || parsed < 1) {
        return 1;
    }
    if (parsed > 38) {
        return 38;
    }
    return Math.floor(parsed);
}

function highlightCustomQuickButtons(value) {
    document.querySelectorAll('#analytics-custom-content .control-button').forEach(button => {
        const target = Number(button.dataset.window);
        button.classList.toggle('active', target === Number(value));
    });
}

function updateCustomSummaryDisplay(data) {
    const summary = document.getElementById('analyticsCustomSummary');
    if (!summary) {
        return;
    }

    const available = data && Array.isArray(data.available_matchdays) ? data.available_matchdays : [];
    const pendingWindow = clampWindow(customClassificationState.pendingWindow || customClassificationState.window || 5);
    const excludedDraft = Array.from(customClassificationState.draftExcluded).sort((a, b) => a - b);
    const includedDraft = available.filter(matchday => !customClassificationState.draftExcluded.has(matchday));
    const excludedApplied = Array.from(customClassificationState.excluded).sort((a, b) => a - b);

    const hasPendingWindowChange = pendingWindow !== clampWindow(customClassificationState.window || pendingWindow);
    const hasPendingExclusions = excludedDraft.length !== excludedApplied.length ||
        excludedDraft.some((value, index) => value !== excludedApplied[index]);

    const includedText = includedDraft.length
        ? includedDraft.map(matchday => `J${matchday}`).join(', ')
        : '—';
    const excludedText = excludedDraft.length
        ? excludedDraft.map(matchday => `J${matchday}`).join(', ')
        : '—';

    summary.innerHTML = `
        <span><strong>Ventana seleccionada:</strong> Últimas ${pendingWindow} jornadas</span>
        <span><strong>Jornadas incluidas:</strong> ${includedText}</span>
        <span><strong>Jornadas excluidas:</strong> ${excludedText}</span>
        ${(hasPendingWindowChange || hasPendingExclusions) ? '<span class="pending-note">Cambios pendientes, pulsa "Aplicar filtros".</span>' : ''}
    `;
}

function renderCustomClassificationControls(data) {
    const windowInput = document.getElementById('analyticsCustomWindow');
    if (windowInput) {
        windowInput.value = clampWindow(customClassificationState.pendingWindow);
    }
    highlightCustomQuickButtons(customClassificationState.pendingWindow);

    const container = document.getElementById('analyticsCustomMatchdays');
    if (!container) {
        return;
    }

    const available = data && Array.isArray(data.available_matchdays) ? data.available_matchdays : [];
    container.innerHTML = '';

    if (!available.length) {
        container.innerHTML = '<span class="pending-note">Sin jornadas disponibles.</span>';
        updateCustomSummaryDisplay(data);
        return;
    }

    available.forEach(matchday => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'matchday-chip';
        button.dataset.matchday = matchday;
        button.textContent = `J${matchday}`;

        if (customClassificationState.draftExcluded.has(matchday)) {
            button.classList.add('active');
        }

        button.addEventListener('click', () => {
            if (customClassificationState.draftExcluded.has(matchday)) {
                customClassificationState.draftExcluded.delete(matchday);
            } else {
                customClassificationState.draftExcluded.add(matchday);
            }
            button.classList.toggle('active');
            updateCustomSummaryDisplay(data);
        });

        container.appendChild(button);
    });

    updateCustomSummaryDisplay(data);
}

function renderCustomClassificationTable(data) {
    const tableId = 'analyticsCustomClassificationTable';
    const emptyNotice = document.getElementById('analytics-custom-empty');
    const classification = data && Array.isArray(data.classification) ? data.classification : [];

    if (!classification.length) {
        populateTable(tableId, ['Pos', 'Equipo', 'Manager', 'PJ', 'PTS', 'Media', 'Tendencia', 'Volatilidad', 'Máx', 'Mín', 'Detalle por jornada'], []);
        if (emptyNotice) {
            emptyNotice.style.display = 'block';
        }
        return;
    }

    if (emptyNotice) {
        emptyNotice.style.display = 'none';
    }

    const rows = classification.map(entry => {
        const matchdayDetails = Array.isArray(entry.matchdays) ? entry.matchdays : [];
        const detailHtml = matchdayDetails.length
            ? matchdayDetails
                .map(item => `<span class="matchday-line">J${item.matchday}: ${formatNumber(item.points || 0, 0)} pts</span>`)
                .join('<br>')
            : '-';

        return [
            entry.rank || 0,
            entry.team_name || entry.team_id || '—',
            entry.username || '—',
            formatNumber(entry.matches_count || 0, 0),
            formatNumber(entry.total_points || 0, 0),
            formatNumber(entry.average_points || 0, 2),
            trendBadge(entry.trend || 0, 2),
            formatNumber(entry.volatility || 0, 2),
            formatNumber(entry.max_points || 0, 0),
            formatNumber(entry.min_points || 0, 0),
            { html: detailHtml, className: 'matchday-detail-cell' }
        ];
    });

    populateTable(tableId, ['Pos', 'Equipo', 'Manager', 'PJ', 'PTS', 'Media', 'Tendencia', 'Volatilidad', 'Máx', 'Mín', 'Detalle por jornada'], rows);
}

async function refreshCustomClassification(showLoading = true) {
    const loading = document.getElementById('analytics-custom-loading');
    const error = document.getElementById('analytics-custom-error');
    const content = document.getElementById('analytics-custom-content');

    if (showLoading && loading) {
        loading.style.display = 'block';
        error.style.display = 'none';
        content.style.display = 'none';
    }

    try {
        customClassificationState.window = clampWindow(customClassificationState.window);
        customClassificationState.pendingWindow = clampWindow(customClassificationState.pendingWindow);
        customClassificationState.excluded = new Set(customClassificationState.draftExcluded);

        const params = {
            window: customClassificationState.window
        };
        if (customClassificationState.excluded.size > 0) {
            params.exclude_matchday = Array.from(customClassificationState.excluded).sort((a, b) => a - b);
        }

        const data = await fetchAnalyticsData(ANALYTICS_ENDPOINTS.customClassification, params);
        analyticsState.caches.custom = data;

        const available = Array.isArray(data.available_matchdays) ? data.available_matchdays.map(Number) : [];
        const excludedFromResponse = Array.isArray(data.excluded_matchdays) ? data.excluded_matchdays.map(Number) : [];
        const validExcluded = excludedFromResponse.filter(matchday => available.includes(matchday));

        customClassificationState.window = clampWindow(data.window || customClassificationState.window);
        customClassificationState.pendingWindow = customClassificationState.window;
        customClassificationState.excluded = new Set(validExcluded);
        customClassificationState.draftExcluded = new Set(validExcluded);

        renderCustomClassificationControls(data);
        renderCustomClassificationTable(data);

        if (loading) {
            loading.style.display = 'none';
        }
        if (error) {
            error.style.display = 'none';
        }
        if (content) {
            content.style.display = 'block';
        }
    } catch (err) {
        console.error('Custom classification fetch error:', err);
        if (loading) {
            loading.style.display = 'none';
        }
        if (content && showLoading) {
            content.style.display = 'none';
        }
        if (error) {
            error.textContent = `No se pudo cargar la clasificación personalizada: ${err.message}`;
            error.style.display = 'block';
        }
        throw err;
    }
}

function initCustomClassificationControls() {
    if (customControlsInitialized) {
        return;
    }

    const windowInput = document.getElementById('analyticsCustomWindow');
    const applyButton = document.getElementById('analyticsCustomApply');
    const resetButton = document.getElementById('analyticsCustomReset');

    if (windowInput) {
        windowInput.addEventListener('input', () => {
            customClassificationState.pendingWindow = clampWindow(windowInput.value || customClassificationState.window);
            highlightCustomQuickButtons(customClassificationState.pendingWindow);
            updateCustomSummaryDisplay(getCurrentCustomData());
        });
    }

    document.querySelectorAll('#analytics-custom-content .control-button').forEach(button => {
        button.addEventListener('click', () => {
            const newWindow = clampWindow(button.dataset.window || customClassificationState.window);
            customClassificationState.pendingWindow = newWindow;
            if (windowInput) {
                windowInput.value = newWindow;
            }
            highlightCustomQuickButtons(newWindow);
            updateCustomSummaryDisplay(getCurrentCustomData());
        });
    });

    if (applyButton) {
        applyButton.addEventListener('click', () => {
            if (windowInput) {
                customClassificationState.pendingWindow = clampWindow(windowInput.value || customClassificationState.window);
            }
            customClassificationState.window = customClassificationState.pendingWindow;
            refreshCustomClassification(true).catch(() => {});
        });
    }

    if (resetButton) {
        resetButton.addEventListener('click', () => {
            customClassificationState.draftExcluded.clear();
            customClassificationState.excluded.clear();
            customClassificationState.pendingWindow = customClassificationState.window;
            if (windowInput) {
                windowInput.value = customClassificationState.window;
            }
            highlightCustomQuickButtons(customClassificationState.pendingWindow);
            updateCustomSummaryDisplay(getCurrentCustomData());
            refreshCustomClassification(true).catch(() => {});
        });
    }

    customControlsInitialized = true;
}

async function loadAnalyticsCustom() {
    const loading = document.getElementById('analytics-custom-loading');
    const error = document.getElementById('analytics-custom-error');
    const content = document.getElementById('analytics-custom-content');

    if (loading) {
        loading.style.display = 'block';
    }
    if (error) {
        error.style.display = 'none';
    }
    if (content) {
        content.style.display = 'none';
    }

    if (!customControlsInitialized) {
        initCustomClassificationControls();
    }

    try {
        customClassificationState.pendingWindow = clampWindow(customClassificationState.window);
        await refreshCustomClassification(false);
        analyticsState.loaded.custom = true;
        if (loading) {
            loading.style.display = 'none';
        }
        if (error) {
            error.style.display = 'none';
        }
        if (content) {
            content.style.display = 'block';
        }
    } catch (err) {
        if (loading) {
            loading.style.display = 'none';
        }
        if (error) {
            error.textContent = `No se pudo cargar la clasificación personalizada: ${err.message}`;
            error.style.display = 'block';
        }
    }
}

function renderMomentumChart(trends) {
    const ctx = document.getElementById('analyticsMomentumChart');
    if (!ctx || !trends || !Array.isArray(trends.teams)) {
        return;
    }

    const sortedTeams = [...trends.teams]
        .sort((a, b) => (b.momentum || 0) - (a.momentum || 0))
        .slice(0, 10);

    const labels = sortedTeams.map(team => team.team_name);
    const data = sortedTeams.map(team => Number((team.momentum || 0).toFixed(3)));

    if (analyticsMomentumChart) {
        analyticsMomentumChart.destroy();
    }

    analyticsMomentumChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Momentum promedio',
                data,
                backgroundColor: '#32CD32',
                borderColor: '#000000',
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatNumber(value, 2)
                    }
                }
            }
        }
    });
}

function renderHeatmapTable(heatmapData, trends) {
    const matchdays = heatmapData && Array.isArray(heatmapData.matchdays) ? heatmapData.matchdays : [];
    const teams = trends && Array.isArray(trends.teams) ? trends.teams : [];

    if (!matchdays.length || !teams.length) {
        populateTable('analyticsHeatmapTable', ['Jornada'], []);
        return;
    }

    const sortedTeams = [...teams].sort((a, b) => (b.total_points || 0) - (a.total_points || 0));
    const displayTeams = sortedTeams.slice(0, Math.min(8, sortedTeams.length));
    const headers = ['Jornada', ...displayTeams.map(team => team.team_name)];

    let maxValue = 0;
    matchdays.forEach(entry => {
        displayTeams.forEach(team => {
            const value = entry.scores ? entry.scores[team.team_id] : undefined;
            if (value !== undefined && value !== null) {
                maxValue = Math.max(maxValue, Math.abs(value));
            }
        });
    });

    const rows = matchdays.map(entry => {
        const row = [{ text: `J${entry.matchday}` }];
        displayTeams.forEach(team => {
            const value = entry.scores ? entry.scores[team.team_id] : null;
            if (value === null || value === undefined) {
                row.push({ text: '-' });
            } else {
                const intensity = maxValue ? Math.min(1, Math.abs(value) / maxValue) : 0;
                const isPositive = value >= 0;
                const backgroundColor = isPositive
                    ? `rgba(50, 205, 50, ${0.15 + intensity * 0.6})`
                    : `rgba(220, 53, 69, ${0.15 + intensity * 0.6})`;
                const textColor = intensity > 0.6 ? '#fff' : '#000';
                row.push({
                    text: formatNumber(value, 0),
                    className: 'heatmap-cell',
                    style: {
                        backgroundColor,
                        color: textColor,
                        fontWeight: '600'
                    }
                });
            }
        });
        return row;
    });

    populateTable('analyticsHeatmapTable', headers, rows);
}

function renderTrendsTable(trends) {
    if (!trends || !Array.isArray(trends.teams)) {
        populateTable('analyticsTrendsTable', ['Equipo'], []);
        return;
    }

    const sortedTeams = [...trends.teams]
        .sort((a, b) => (b.total_points || 0) - (a.total_points || 0))
        .slice(0, 15);

    const rows = sortedTeams.map(team => [
        team.team_name,
        formatNumber(team.total_points || 0, 0),
        trendBadge(team.position_delta || 0, 0),
        formatNumber(team.average_points || 0, 2),
        trendBadge(team.momentum || 0, 3)
    ]);

    populateTable('analyticsTrendsTable', ['Equipo', 'Puntos Totales', 'Δ Posición', 'Media Jornada', 'Momentum'], rows);
}

async function loadAnalyticsPlayers() {
    if (!canAccessAnalyticsSection('players')) {
        lockAnalyticsSection('players');
        return;
    }

    const loading = document.getElementById('analytics-players-loading');
    const error = document.getElementById('analytics-players-error');
    const content = document.getElementById('analytics-players-content');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    try {
        const [formData, valueData] = await Promise.all([
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.playerForm, { window: 5 }),
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.playerValue, { window: 30 })
        ]);

        renderPlayerFormTable(formData);
        renderPlayerValueTable(valueData);

        analyticsState.loaded.players = true;
        loading.style.display = 'none';
        content.style.display = 'grid';
    } catch (err) {
        console.error('Player analytics error:', err);
        loading.style.display = 'none';
        error.textContent = `No se pudo cargar el análisis de jugadores: ${err.message}`;
        error.style.display = 'block';
    }
}

function renderPlayerFormTable(formData) {
    const players = formData && Array.isArray(formData.players)
        ? [...formData.players].sort((a, b) => (b.average_points || 0) - (a.average_points || 0)).slice(0, 20)
        : [];

    const rows = players.map((player, index) => [
        index + 1,
        player.name || 'Desconocido',
        player.matches || 0,
        formatNumber(player.average_points || 0, 2),
        trendBadge(player.trend || 0, 2),
        player.last_matchday ? `J${player.last_matchday}` : '-'
    ]);

    populateTable('analyticsPlayerFormTable', ['Pos', 'Jugador', 'Partidos', 'Promedio', 'Tendencia', 'Última Jornada'], rows);
}

function renderPlayerValueTable(valueData) {
    const players = valueData && Array.isArray(valueData.players)
        ? [...valueData.players].sort((a, b) => (b.variation || 0) - (a.variation || 0)).slice(0, 20)
        : [];

    const rows = players.map((player, index) => {
        const variation = player.variation || 0;
        const variationCell = variation === 0
            ? { text: formatMoney(0) }
            : variation > 0
                ? { html: `<span class="analytics-pill badge-easy">▲ ${formatMoney(variation)}</span>` }
                : { html: `<span class="analytics-pill badge-hard">▼ ${formatMoney(Math.abs(variation))}</span>` };
        return [
            index + 1,
            player.name || 'Desconocido',
            formatMoney(player.average_market_price || 0),
            formatMoney(player.latest_price || 0),
            variationCell,
            player.clause_price !== null && player.clause_price !== undefined ? formatMoney(player.clause_price) : '-',
            player.suggested_clause !== null && player.suggested_clause !== undefined ? formatMoney(player.suggested_clause) : '-',
            formatNumber(player.average_last_five || 0, 2),
            formatNumber(player.average_overall || 0, 2)
        ];
    });

    populateTable('analyticsPlayerValueTable', ['Pos', 'Jugador', 'Precio Medio', 'Precio Actual', 'Variación', 'Cláusula', 'Sugerida', 'Promedio Últimos 5', 'Promedio Total'], rows);
}

async function loadAnalyticsUsers() {
    if (!canAccessAnalyticsSection('users')) {
        lockAnalyticsSection('users');
        return;
    }

    const loading = document.getElementById('analytics-users-loading');
    const error = document.getElementById('analytics-users-error');
    const content = document.getElementById('analytics-users-content');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    try {
        const [consistencyData, marketData] = await Promise.all([
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.userConsistency, { window: 10 }),
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.userMarketActivity, { window_days: 30 })
        ]);

        renderConsistencyChart(consistencyData);
        renderMarketActivityTable(marketData);

        analyticsState.loaded.users = true;
        loading.style.display = 'none';
        content.style.display = 'block';
    } catch (err) {
        console.error('User analytics error:', err);
        loading.style.display = 'none';
        error.textContent = `No se pudo cargar el análisis de usuarios: ${err.message}`;
        error.style.display = 'block';
    }
}

function renderConsistencyChart(data) {
    const ctx = document.getElementById('analyticsConsistencyChart');
    if (!ctx || !data || !Array.isArray(data.teams)) {
        return;
    }

    const sortedTeams = [...data.teams]
        .sort((a, b) => (b.consistency_index || 0) - (a.consistency_index || 0))
        .slice(0, 12);

    const labels = sortedTeams.map(team => team.team_name);
    const values = sortedTeams.map(team => Number((team.consistency_index || 0).toFixed(4)));

    if (analyticsConsistencyChart) {
        analyticsConsistencyChart.destroy();
    }

    const colors = generateColors(labels.length);
    analyticsConsistencyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Índice de consistencia',
                data: values,
                backgroundColor: colors,
                borderColor: '#000000',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: value => formatNumber(value, 2)
                    }
                }
            }
        }
    });
}

function renderMarketActivityTable(marketData) {
    const teams = marketData && Array.isArray(marketData.teams)
        ? [...marketData.teams].sort((a, b) => (b.transactions || 0) - (a.transactions || 0))
        : [];

    const rows = teams.map(team => [
        team.team_name || 'Desconocido',
        team.transactions || 0,
        formatMoney(team.spent || 0),
        formatMoney(team.received || 0),
        `${team.clauses_paid || 0} (${formatMoney(team.clause_total_paid || 0)})`,
        `${team.clauses_received || 0} (${formatMoney(team.clause_total_received || 0)})`
    ]);

    populateTable('analyticsMarketActivityTable', ['Equipo', 'Transacciones', 'Gastado', 'Recibido', 'Cláusulas Pagadas', 'Cláusulas Recibidas'], rows);
}

async function loadAnalyticsMarket() {
    if (!canAccessAnalyticsSection('market')) {
        lockAnalyticsSection('market');
        return;
    }

    const loading = document.getElementById('analytics-market-loading');
    const error = document.getElementById('analytics-market-error');
    const content = document.getElementById('analytics-market-content');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    try {
        const [watchlistData, clauseData] = await Promise.all([
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.watchlist, { limit: 30 }),
            fetchAnalyticsData(ANALYTICS_ENDPOINTS.clauseNetwork)
        ]);

        renderWatchlistTable(watchlistData);
        renderClauseNetworkTable(clauseData);

        analyticsState.loaded.market = true;
        loading.style.display = 'none';
        content.style.display = 'grid';
    } catch (err) {
        console.error('Market analytics error:', err);
        loading.style.display = 'none';
        error.textContent = `No se pudo cargar el análisis de mercado: ${err.message}`;
        error.style.display = 'block';
    }
}

function renderWatchlistTable(watchlistData) {
    const players = watchlistData && Array.isArray(watchlistData.players)
        ? [...watchlistData.players].slice(0, 20)
        : [];

    const rows = players.map((player, index) => [
        index + 1,
        player.player_name || 'Desconocido',
        player.owner_name || 'Agente libre',
        formatNumber(player.value_score || 0, 4),
        player.clause_price !== null && player.clause_price !== undefined ? formatMoney(player.clause_price) : '-',
        player.suggested_clause !== null && player.suggested_clause !== undefined ? formatMoney(player.suggested_clause) : '-',
        formatNumber(player.average_last_five || 0, 2),
        formatNumber(player.average_overall || 0, 2)
    ]);

    populateTable('analyticsWatchlistTable', ['Pos', 'Jugador', 'Dueño', 'Score', 'Cláusula Actual', 'Cláusula Sugerida', 'Promedio Últimos 5', 'Promedio Total'], rows);
}

function renderClauseNetworkTable(clauseData) {
    const edges = clauseData && Array.isArray(clauseData.edges)
        ? [...clauseData.edges].sort((a, b) => (b.total_amount || 0) - (a.total_amount || 0)).slice(0, 20)
        : [];

    const rows = edges.map(edge => [
        edge.source_name || edge.source || '-',
        edge.target_name || edge.target || '-',
        edge.count || 0,
        formatMoney(edge.total_amount || 0)
    ]);

    populateTable('analyticsClausesNetworkTable', ['Desde', 'Hacia', 'Veces', 'Importe'], rows);
}

async function loadAnalyticsOpportunities() {
    if (!canAccessAnalyticsSection('opportunities')) {
        lockAnalyticsSection('opportunities');
        return;
    }

    const loading = document.getElementById('analytics-opportunities-loading');
    const error = document.getElementById('analytics-opportunities-error');
    const content = document.getElementById('analytics-opportunities-content');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    try {
        const data = await fetchAnalyticsData(ANALYTICS_ENDPOINTS.streaks, { min_streak: 3, threshold: 6 });
        const streaks = data && Array.isArray(data.streaks)
            ? [...data.streaks].sort((a, b) => (b.streak_length || 0) - (a.streak_length || 0)).slice(0, 25)
            : [];

        const rows = streaks.map((streak, index) => [
            index + 1,
            streak.name || 'Desconocido',
            streak.streak_length || 0,
            formatNumber(streak.average_points || 0, 2),
            (streak.points || []).join(', '),
            (streak.matchdays || []).map(md => `J${md}`).join(', ')
        ]);

        populateTable('analyticsStreaksTable', ['Pos', 'Jugador', 'Racha', 'Promedio', 'Puntos', 'Jornadas'], rows);

        analyticsState.loaded.opportunities = true;
        loading.style.display = 'none';
        content.style.display = 'block';
    } catch (err) {
        console.error('Opportunities analytics error:', err);
        loading.style.display = 'none';
        error.textContent = `No se pudo cargar las oportunidades: ${err.message}`;
        error.style.display = 'block';
    }
}

async function loadAnalyticsProjections() {
    if (!canAccessAnalyticsSection('projections')) {
        lockAnalyticsSection('projections');
        return;
    }

    const loading = document.getElementById('analytics-projections-loading');
    const error = document.getElementById('analytics-projections-error');
    const content = document.getElementById('analytics-projections-content');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    try {
        const data = await fetchAnalyticsData(ANALYTICS_ENDPOINTS.projections);
        renderProjectionsList(data);
        analyticsState.loaded.projections = true;
        loading.style.display = 'none';
        content.style.display = 'block';
    } catch (err) {
        console.error('Projections analytics error:', err);
        loading.style.display = 'none';
        error.textContent = `No se pudo cargar las proyecciones: ${err.message}`;
        error.style.display = 'block';
    }
}

function renderProjectionsList(projectionsData) {
    const container = document.getElementById('analyticsProjectionsList');
    if (!container) {
        return;
    }

    container.innerHTML = '';
    const matches = projectionsData && Array.isArray(projectionsData.matches) ? projectionsData.matches : [];

    if (!matches.length) {
        const empty = document.createElement('p');
        empty.textContent = 'No hay partidos disponibles para proyectar.';
        container.appendChild(empty);
        return;
    }

    matches.forEach(match => {
        const card = document.createElement('div');
        card.className = 'projection-card';

        const matchDate = match.match_date ? new Date(match.match_date) : null;
        const dateText = matchDate ? matchDate.toLocaleString('es-ES', { dateStyle: 'medium', timeStyle: 'short' }) : 'Por confirmar';

        const homeBadge = getDifficultyBadge(match.home && match.home.difficulty);
        const awayBadge = getDifficultyBadge(match.away && match.away.difficulty);

        card.innerHTML = `
            <h3>J${match.matchday || projectionsData.target_matchday || '-'} · ${dateText}</h3>
            <div class="teams">
                <span>${match.home ? match.home.team_name : 'Local'}</span>
                <span>${match.away ? match.away.team_name : 'Visitante'}</span>
            </div>
            <div class="difficulty">
                <span class="projection-badge ${homeBadge.className}">${homeBadge.label}</span>
                <span class="projection-badge ${awayBadge.className}">${awayBadge.label}</span>
            </div>
        `;

        container.appendChild(card);
    });
}

function getDifficultyBadge(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
        return { label: 'Sin datos', className: 'badge-medium' };
    }
    const numericValue = Number(value);
    const formatted = formatNumber(Math.abs(numericValue), 3);
    if (numericValue <= -0.1) {
        return { label: `Favorable · ${formatted}`, className: 'badge-easy' };
    }
    if (numericValue >= 0.1) {
        return { label: `Complicado · ${formatted}`, className: 'badge-hard' };
    }
    return { label: `Neutral · ${formatted}`, className: 'badge-medium' };
}

// ==================== PRESUPUESTO (Tab principal) ====================

let budgetLoaded = false;

async function syncTransactions() {
    const btn = document.getElementById('budgetSyncBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Sincronizando...';
    
    try {
        const response = await fetch('/api/v1/sync/trigger?sync_type=transactions', { method: 'POST' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const synced = data.results?.transactions?.records_synced || 0;
        btn.textContent = `✅ ${synced} nuevas`;
        
        // Recargar datos de presupuesto
        budgetLoaded = false;
        await loadBudgetTab();
    } catch (err) {
        btn.textContent = '❌ Error';
        console.error('Sync error:', err);
    }
    
    setTimeout(() => {
        btn.disabled = false;
        btn.textContent = '🔄 Sincronizar';
    }, 3000);
}

async function loadBudgetTab() {
    if (budgetLoaded) return;
    
    const loading = document.getElementById('budgetLoading');
    const error = document.getElementById('budgetError');
    const content = document.getElementById('budgetContent');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    try {
        const response = await fetch(ANALYTICS_ENDPOINTS.balances);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        renderBudgetTable(data);
        budgetLoaded = true;
        loading.style.display = 'none';
        content.style.display = 'block';
    } catch (err) {
        console.error('Budget load error:', err);
        loading.style.display = 'none';
        error.textContent = `No se pudo cargar los presupuestos: ${err.message}`;
        error.style.display = 'block';
    }
}

function renderBudgetTable(data) {
    const container = document.getElementById('budgetTable');
    const detailContainer = document.getElementById('budgetDetail');
    if (!container) return;

    container.style.display = 'block';
    detailContainer.style.display = 'none';

    const teams = data.teams || [];
    if (!teams.length) {
        container.innerHTML = '<p>No hay datos de transacciones disponibles.</p>';
        return;
    }

    let html = `<table class="analytics-table balances-table">
        <thead>
            <tr>
                <th>Equipo</th>
                <th>Saldo</th>
                <th>Valor Plantilla</th>
                <th>Gastado</th>
                <th>Ingresado</th>
                <th>Ops</th>
                <th>Rendimiento</th>
            </tr>
        </thead>
        <tbody>`;

    teams.forEach(team => {
        const balanceClass = team.balance >= data.initial_budget ? 'balance-positive' : 
                            team.balance >= data.initial_budget * 0.5 ? 'balance-neutral' : 'balance-negative';
        const perfClass = team.performance >= 0 ? 'perf-positive' : 'perf-negative';
        const perfSign = team.performance >= 0 ? '+' : '';
        html += `
            <tr class="clickable-row" onclick="loadBudgetDetail('${team.team_id}', '${team.team_name.replace(/'/g, "\\'")}')">
                <td><strong>${team.team_name}</strong></td>
                <td class="${balanceClass}">${formatMoney(team.balance)}</td>
                <td>${formatMoney(team.team_value)}</td>
                <td class="money-spent">-${formatMoney(team.total_spent)}</td>
                <td class="money-income">+${formatMoney(team.total_income)}</td>
                <td>${team.purchases_count + team.sales_count}</td>
                <td class="${perfClass}">${perfSign}${formatMoney(team.performance)}</td>
            </tr>`;
    });

    html += '</tbody></table>';
    html += '<p style="color:#888; font-size:0.8em; margin-top:8px;">Rendimiento = Valor plantilla − (Gastado − Ingresado). Positivo = plantilla vale más de lo invertido neto.</p>';
    container.innerHTML = html;
}

async function loadBudgetDetail(teamId, teamName) {
    const tableContainer = document.getElementById('budgetTable');
    const detailContainer = document.getElementById('budgetDetail');
    const detailContent = document.getElementById('budgetDetailContent');

    tableContainer.style.display = 'none';
    detailContainer.style.display = 'block';
    detailContent.innerHTML = '<div class="loading">Cargando detalle...</div>';

    try {
        const response = await fetch(`${ANALYTICS_ENDPOINTS.balances}/${teamId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        renderBudgetDetail(data);
    } catch (err) {
        detailContent.innerHTML = `<p class="error">Error cargando detalle: ${err.message}</p>`;
    }
}

function renderBudgetDetail(data) {
    const container = document.getElementById('budgetDetailContent');

    const balanceClass = data.balance >= data.initial_budget ? 'balance-positive' : 
                        data.balance >= data.initial_budget * 0.5 ? 'balance-neutral' : 'balance-negative';

    let html = `
        <h3>💰 ${data.team_name}</h3>
        <div class="balance-summary">
            <span class="balance-label">Saldo actual:</span>
            <span class="balance-value ${balanceClass}">${formatMoney(data.balance)}</span>
            <span class="balance-detail">(Gastado: ${formatMoney(data.total_spent)} | Ingresado: ${formatMoney(data.total_income)})</span>
        </div>
    `;

    // Altas (compras)
    html += '<h4>📥 Altas (Compras) — ' + data.purchases.length + '</h4>';
    if (data.purchases.length) {
        html += `<table class="analytics-table balances-table">
            <thead><tr><th>Jugador</th><th>Precio</th><th>Procedencia</th><th>Fecha</th></tr></thead>
            <tbody>`;
        data.purchases.forEach(p => {
            const date = p.date ? new Date(p.date).toLocaleDateString('es-ES') : '-';
            html += `<tr>
                <td>${p.player_name}</td>
                <td class="money-spent">${formatMoney(p.price)}</td>
                <td>${p.from}</td>
                <td>${date}</td>
            </tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p>No hay compras registradas.</p>';
    }

    // Bajas (ventas)
    html += '<h4>📤 Bajas (Ventas) — ' + data.sales.length + '</h4>';
    if (data.sales.length) {
        html += `<table class="analytics-table balances-table">
            <thead><tr><th>Jugador</th><th>Precio</th><th>Destino</th><th>Fecha</th></tr></thead>
            <tbody>`;
        data.sales.forEach(s => {
            const date = s.date ? new Date(s.date).toLocaleDateString('es-ES') : '-';
            html += `<tr>
                <td>${s.player_name}</td>
                <td class="money-income">${formatMoney(s.price)}</td>
                <td>${s.to}</td>
                <td>${date}</td>
            </tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p>No hay ventas registradas.</p>';
    }

    container.innerHTML = html;
}

function hideBudgetDetail() {
    document.getElementById('budgetTable').style.display = 'block';
    document.getElementById('budgetDetail').style.display = 'none';
}

function formatMoney(amount) {
    if (amount === null || amount === undefined) return '-';
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(amount);
}

async function attemptLogin(username, password) {
    const response = await fetch(AUTH_ENDPOINTS.login, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
        let detail = 'Credenciales incorrectas';
        try {
            const payload = await response.json();
            if (payload && payload.detail) {
                detail = payload.detail;
            }
        } catch (error) {
            // ignore JSON parse errors
        }
        throw new Error(detail);
    }

    return response.json();
}

async function validateSession(token) {
    const response = await fetch(`${AUTH_ENDPOINTS.session}?token=${encodeURIComponent(token)}`);
    if (!response.ok) {
        throw new Error('Sesión no válida');
    }
    return response.json();
}

async function startAppIfNeeded() {
    if (appInitialized) {
        return;
    }
    await init();
    appInitialized = true;
}

async function handleLoginSubmit(event) {
    event?.preventDefault?.();
    const loginButton = document.getElementById('login-button');
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const loginError = document.getElementById('login-error');
    const loginForm = document.getElementById('login-form');

    if (loginError) {
        loginError.textContent = '';
        loginError.style.display = 'none';
    }

    const username = usernameInput?.value?.trim() || '';
    const password = passwordInput?.value || '';

    if (!username || !password) {
        const message = 'Introduce usuario y contraseña.';
        if (loginError) {
            loginError.textContent = message;
            loginError.style.display = 'block';
        } else {
            showAccessMessage(message, 'global', 4000);
        }
        return;
    }

    if (loginButton) {
        loginButton.disabled = true;
    }
    if (usernameInput) {
        usernameInput.disabled = true;
    }
    if (passwordInput) {
        passwordInput.disabled = true;
    }

    let loginSucceeded = false;
    try {
        const result = await attemptLogin(username, password);
        loginSucceeded = true;
        if (loginForm) {
            loginForm.reset();
        }
        resetAppState();
        setAuthState({
            isAuthenticated: true,
            username: result.username,
            role: result.role,
            token: result.token,
            expiresAt: result.expires_at
        });
        hideLoginView();
        await startAppIfNeeded();
        showTab('evolution');
        showAnalyticsSection('overview');
        showAccessMessage(`Sesión iniciada como ${result.username}.`);
        hideAccessMessage('analytics');
    } catch (error) {
        const message = error.message || 'Credenciales incorrectas';
        if (loginError) {
            loginError.textContent = message;
            loginError.style.display = 'block';
        }
        showAccessMessage(message, 'global', 5000);
    } finally {
        if (loginButton) {
            loginButton.disabled = false;
        }
        if (!authState.isAuthenticated) {
            if (usernameInput) {
                usernameInput.disabled = false;
                if (!loginSucceeded) {
                    usernameInput.focus();
                }
            }
            if (passwordInput) {
                passwordInput.disabled = false;
                passwordInput.value = '';
            }
        }
    }
}

async function logout() {
    if (authState.token) {
        try {
            await fetch(`${AUTH_ENDPOINTS.logout}?token=${encodeURIComponent(authState.token)}`, {
                method: 'POST'
            });
        } catch (error) {
            console.warn('No se pudo cerrar la sesión en el servidor:', error);
        }
    }

    clearAuthState();
    resetAppState();
    showAccessMessage('Has cerrado sesión. Estás en modo invitado.');
    await startAppIfNeeded();
    showTab('evolution');
    showAnalyticsSection('overview');
}

function setupAuthEventHandlers() {
    if (authEventsBound) {
        return;
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }

    authEventsBound = true;
}

async function initializeAuth() {
    setupAuthEventHandlers();

    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
        try {
            const parsed = JSON.parse(stored);
            if (parsed && parsed.token) {
                try {
                    const sessionData = await validateSession(parsed.token);
                    resetAppState();
                    setAuthState({
                        isAuthenticated: true,
                        username: sessionData.username,
                        role: sessionData.role,
                        token: parsed.token,
                        expiresAt: sessionData.expires_at
                    });
                    hideLoginView();
                    await startAppIfNeeded();
                    showTab('evolution');
                    showAnalyticsSection('overview');
                    hideAccessMessage('global');
                    hideAccessMessage('analytics');
                    return;
                } catch (error) {
                    console.info('Sesión almacenada inválida, solicitando login nuevamente.');
                    clearAuthState();
                }
            }
        } catch (error) {
            console.warn('No se pudo analizar la sesión almacenada:', error);
        }
    }

    await startAppIfNeeded();
    applyRoleRestrictions();
    showTab('budget');
    showAnalyticsSection('overview');
}

function bootstrap() {
    initializeAuth();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
} else {
    bootstrap();
}
