"""
Main FastAPI application
"""

import os
import ssl

# Disable SSL verification in Docker environments (corporate proxy / cert issues)
if os.getenv("SSL_VERIFY", "1") == "0":
    ssl._create_default_https_context = ssl._create_unverified_context

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from app.services.photo_service import PhotoService
from app.api.v1.endpoints import matchdays
from app.api.v1.endpoints.initialize import router as initialize_router
from app.api.v1.endpoints.reset_db import router as reset_db_router
from app.api.v1.endpoints.statistics import router as statistics_router
from app.api.v1.endpoints.player_finances import router as player_finances_router
from app.api.v1.endpoints.user_stats import router as user_stats_router
from app.api.v1.endpoints.clausulable_players import router as clausulable_players_router
from app.api.v1.endpoints.sync import router as sync_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.balances import router as balances_router
from app.api.v1.endpoints.championships import router as championships_router
from app.api.v1.endpoints.phantoms import router as phantoms_router
from app.api.v1.endpoints.market import router as market_router
from app.api.v1.endpoints.roster import router as roster_router
from app.api.v1.endpoints.favorites import router as favorites_router
from app.api.v1.endpoints.transactions import router as transactions_router
from app.api.v1.endpoints.sofascore_sync import router as sofascore_sync_router
from app.api.v1.endpoints.sofascore_detail import router as sofascore_detail_router
from app.api.v1.endpoints.user import router as user_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Futmondo API service...")
    yield
    logger.info("Shutting down Futmondo API service...")

# Create FastAPI app
app = FastAPI(
    title="Futmondo API",
    description="API for analyzing Futmondo player transactions and team evolution",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware - allow frontend origin
# Allow all origins when accessed through ngrok or localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (ngrok domains change)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth middleware: protect /api/v1/* routes ---
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.auth.jwt_utils import verify_token
from app.auth.token_store import init_auth_tables

# Public paths that don't require authentication
AUTH_EXCLUDED_PATHS = {"/auth/login", "/auth/refresh", "/auth/logout", "/health", "/", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        
        # Skip auth for non-API routes, auth routes, health, and docs
        if not path.startswith("/api/v1") and not path.startswith("/auth"):
            return await call_next(request)
        
        if any(path.endswith(excluded) for excluded in AUTH_EXCLUDED_PATHS):
            return await call_next(request)
        
        if path.startswith("/auth"):
            return await call_next(request)
        
        # Require Bearer token for all other /api/v1/* routes
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = auth_header.split(" ", 1)[1]
        payload = verify_token(token, expected_type="access")
        if not payload:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token expired or invalid"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Attach user info to request state for downstream use
        request.state.user = {
            "user_id": payload["sub"],
            "email": payload.get("email", ""),
            "futmondo_uid": payload.get("futmondo_uid", ""),
        }
        
        return await call_next(request)


app.add_middleware(AuthMiddleware)

# Initialize auth tables on startup
try:
    init_auth_tables()
except Exception as e:
    logger.warning(f"Could not init auth tables at import time: {e}")

# Include auth router (no /api/v1 prefix — lives at /auth/*)
from app.auth.routes import router as auth_router
app.include_router(auth_router)

# Include routers
app.include_router(matchdays.router, prefix="/api/v1/matchdays", tags=["matchdays"])
app.include_router(initialize_router, prefix="/api/v1/initialize", tags=["initialize"])
app.include_router(reset_db_router, prefix="/api/v1/database", tags=["database"])
app.include_router(statistics_router, prefix="/api/v1/statistics", tags=["statistics"])
app.include_router(player_finances_router, prefix="/api/v1/player-finances", tags=["player-finances"])
app.include_router(user_stats_router, prefix="/api/v1/user-stats", tags=["user-stats"])
app.include_router(clausulable_players_router, prefix="/api/v1/clausulable-players", tags=["clausulable-players"])
app.include_router(sync_router, prefix="/api/v1/sync", tags=["sync"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(balances_router, prefix="/api/v1/analytics", tags=["balances"])
app.include_router(championships_router, prefix="/api/v1", tags=["championships"])
app.include_router(phantoms_router, prefix="/api/v1/sync", tags=["phantoms"])
app.include_router(market_router, prefix="/api/v1/market", tags=["market"])
app.include_router(roster_router, prefix="/api/v1/roster", tags=["roster"])
app.include_router(favorites_router, prefix="/api/v1/favorites", tags=["favorites"])
app.include_router(transactions_router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(sofascore_sync_router, prefix="/api/v1/sync", tags=["sofascore"])
app.include_router(sofascore_detail_router, prefix="/api/v1/sofascore", tags=["sofascore"])
app.include_router(user_router, prefix="/api/v1/user", tags=["user"])

# Also serve routes without /api prefix (to avoid redirect loops)
# Include the same router with the old prefix
app.include_router(matchdays.router, prefix="/v1/matchdays", tags=["matchdays"])

# Serve static photos
photos_dir = Path("static/photos/players")
photos_dir.mkdir(parents=True, exist_ok=True)

# Mount static files for photos - BEST PRACTICE: serve static files directly
try:
    app.mount("/static/photos", StaticFiles(directory=str(photos_dir)), name="photos")
    logger.info(f"✅ Static photos mounted at /static/photos from {photos_dir}")
except Exception as e:
    logger.warning(f"Could not mount static photos: {e}")

@app.get("/api/v1/photos/{player_id}")
async def get_player_photo(player_id: str, request: Request):
    """Serve player photo from local storage or fetch from Futmondo API"""
    from app.services.db_connection import DBConnection
    import requests
    
    # Validate player_id
    if not player_id or player_id == "default":
        # Return SVG placeholder for default/empty IDs
        from fastapi.responses import Response
        svg_placeholder = """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
            <rect width="100" height="100" fill="#c8c8c8"/>
            <text x="50" y="50" font-family="Arial" font-size="40" fill="#808080" 
                  text-anchor="middle" dominant-baseline="central">?</text>
        </svg>"""
        return Response(content=svg_placeholder, media_type="image/svg+xml")
    
    logger.debug(f"Photo request for player_id: {player_id}")
    
    photo_service = PhotoService()
    db = DBConnection()
    
    # First check if photo exists locally via photo_service
    photo_path = photo_service.get_photo_path(player_id)
    if photo_path and os.path.exists(photo_path):
        logger.info(f"Serving local photo: {photo_path} for player {player_id}")
        # Determine content type from file extension
        ext = os.path.splitext(photo_path)[1].lower()
        media_type = "image/jpeg"  # default
        if ext == ".png":
            media_type = "image/png"
        elif ext == ".webp":
            media_type = "image/webp"
        # Return redirect to static file - BEST PRACTICE
        # This allows browser caching and better performance
        from fastapi.responses import RedirectResponse
        filename = os.path.basename(photo_path)
        static_url = f"/static/photos/{filename}"
        logger.debug(f"Redirecting to static file: {static_url}")
        return RedirectResponse(url=static_url, status_code=302)
    
    # Try to get photo URL from database - EFFICIENT: single connection
    photo_url = None
    photo_local_path = None
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Try player_photos table first
        sql = "SELECT photo_url, local_path FROM player_photos WHERE player_id = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (player_id,))
        result = cursor.fetchone()
        
        if result:
            photo_url, photo_local_path = result
            
            # Try local path first if exists
            if photo_local_path and os.path.exists(photo_local_path):
                from fastapi.responses import RedirectResponse
                filename = os.path.basename(photo_local_path)
                return RedirectResponse(url=f"/static/photos/{filename}", status_code=302)
        else:
            # Fallback: check players table
            sql = "SELECT photo_url, photo_local_path FROM players WHERE id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (player_id,))
            result = cursor.fetchone()
            
            if result:
                photo_url, photo_local_path = result
                
                # Try local path first if exists
                if photo_local_path and os.path.exists(photo_local_path):
                    from fastapi.responses import RedirectResponse
                    filename = os.path.basename(photo_local_path)
                    return RedirectResponse(url=f"/static/photos/{filename}", status_code=302)
    
    # If we have a URL, try to download it using photo_service - EFFICIENT: uses optimized methods
    if photo_url:
        try:
            # Use photo_service to download - it handles multiple URL formats and DB operations efficiently
            player_data = {"photo": photo_url}  # Minimal data for photo_service
            local_path = photo_service.process_player_photo(player_data, player_id)
            
            if local_path and os.path.exists(local_path):
                logger.info(f"Successfully downloaded photo for player {player_id}: {local_path}")
                # Serve via redirect to static file
                from fastapi.responses import RedirectResponse
                filename = os.path.basename(local_path)
                return RedirectResponse(url=f"/static/photos/{filename}", status_code=302)
        except Exception as e:
            logger.error(f"Failed to download photo for player {player_id}: {e}")
    
    # Last resort: Try downloading with player_id directly (if we don't have URL)
    # Futmondo photos are often named as {player_id}.png
    if not photo_url:
        logger.debug(f"No photo URL in DB for player {player_id}, trying direct download with player_id")
        try:
            player_data = {}  # Empty data, will try player_id directly
            local_path = photo_service.process_player_photo(player_data, player_id)
            
            if local_path and os.path.exists(local_path):
                from fastapi.responses import RedirectResponse
                filename = os.path.basename(local_path)
                return RedirectResponse(url=f"/static/photos/{filename}", status_code=302)
        except Exception as e:
            logger.debug(f"Direct download with player_id also failed for {player_id}: {e}")
    
    # Return SVG placeholder if no photo available
    from fastapi.responses import Response
    svg_placeholder = """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect width="100" height="100" fill="#c8c8c8"/>
        <text x="50" y="50" font-family="Arial" font-size="40" fill="#808080" 
              text-anchor="middle" dominant-baseline="central">?</text>
    </svg>"""
    return Response(content=svg_placeholder, media_type="image/svg+xml")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Futmondo API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
    }

