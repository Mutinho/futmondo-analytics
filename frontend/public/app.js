/**
 * Main application JavaScript - Enhanced with interactive tooltips
 */

const API_URL = '/api/v1/matchdays';
const FINANCES_API_URL = '/api/v1/player-finances/';  // Add trailing slash to avoid 307 redirects
const USER_STATS_API_URL = '/api/v1/user-stats/';  // Add trailing slash to avoid 307 redirects
const CLAUSULABLE_PLAYERS_API_URL = '/api/v1/clausulable-players/';  // Add trailing slash to avoid 307 redirects

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
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tabElement = document.getElementById(`${tabName}-tab`);
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    // Add active class to button
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => {
        const btnText = btn.textContent.toLowerCase();
        if ((tabName === 'evolution' && btnText.includes('evolución')) ||
            (tabName === 'finances' && btnText.includes('finanzas')) ||
            (tabName === 'stats' && btnText.includes('estadísticas')) ||
            (tabName === 'clausulable' && btnText.includes('clausulables'))) {
            btn.classList.add('active');
        }
    });
    
        // Load data when tab is shown
        if (tabName === 'finances') {
            loadFinancesData();
        } else if (tabName === 'stats') {
            loadUserStatsData();
        } else if (tabName === 'clausulable') {
            loadClausulablePlayersData();
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

/**
 * Load finances data from API
 */
async function loadFinancesData() {
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
    
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
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

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
