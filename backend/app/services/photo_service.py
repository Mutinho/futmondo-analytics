#!/usr/bin/env python3
"""
Photo Service - Downloads and manages player photos locally
"""

import os
import requests
import hashlib
import logging
from typing import Optional, Dict
from pathlib import Path
from app.core.config import DATABASE_PATH
from app.services.db_connection import DBConnection

logger = logging.getLogger(__name__)

class PhotoService:
    """Service for downloading and managing player photos"""
    
    def __init__(self, photos_dir: str = "static/photos/players", db_path: str = None):
        self.photos_dir = Path(photos_dir)
        self.db_path = db_path or DATABASE_PATH
        self.db = DBConnection()
        self.photos_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_photo_url(self, player_data: Dict) -> Optional[str]:
        """Extract photo URL from player data structure
        
        Formats supported:
        - Full URL: https://static01.mondocore.com/futmondo/img/faces/64/93055760.png
        - Relative URL: /img/faces/64/93055760.png
        - Filename only: 93055760.png or 67196000.png
        """
        # Base URL for Futmondo photos
        PHOTO_BASE_URL = "https://static01.mondocore.com/futmondo/img/faces/64"
        
        # Try different possible keys for photo URL
        possible_keys = [
            'photo', 'photoUrl', 'photo_url', 'image', 'imageUrl', 'image_url',
            'avatar', 'avatarUrl', 'avatar_url', 'picture', 'pictureUrl', 'picture_url',
            'photoUrlMobile', 'photoUrlDesktop'
        ]
        
        for key in possible_keys:
            if key in player_data and player_data[key]:
                url = player_data[key]
                if not isinstance(url, str) or not url:
                    continue
                
                # If it's already a full URL, return it
                if url.startswith('http'):
                    return url
                
                # If it's a relative URL starting with /
                if url.startswith('/'):
                    return f"https://static01.mondocore.com{url}"
                
                # If it's just a filename (e.g., "67196000.png" or "93055760.png")
                # Construct the full URL using the base URL
                if '.' in url and not url.startswith('/'):
                    # Extract the number part if it's in format like "67196000.png"
                    # or use it directly if it's already a valid filename
                    photo_filename = url
                    return f"{PHOTO_BASE_URL}/{photo_filename}"
        
        # Try nested structures
        if 'player' in player_data:
            return self.extract_photo_url(player_data['player'])
        
        if 'photo' in player_data and isinstance(player_data['photo'], dict):
            for key in possible_keys:
                if key in player_data['photo'] and player_data['photo'][key]:
                    url = player_data['photo'][key]
                    if isinstance(url, str) and url:
                        if url.startswith('http'):
                            return url
                        elif url.startswith('/'):
                            return f"https://static01.mondocore.com{url}"
                        elif '.' in url:
                            return f"{PHOTO_BASE_URL}/{url}"
        
        return None
    
    def download_photo(self, photo_url: str, player_id: str) -> Optional[str]:
        """Download photo from URL and save locally - tries multiple URL formats if needed"""
        base_url = "https://static01.mondocore.com/futmondo/img/faces/64"
        urls_to_try = []
        
        # If we have a URL, try it first
        if photo_url:
            # Handle relative URLs - use the correct base URL
            if photo_url.startswith('/'):
                photo_url = f"https://static01.mondocore.com{photo_url}"
            elif not photo_url.startswith('http'):
                # If it's just a filename, construct the full URL
                photo_url = f"{base_url}/{photo_url}"
            
            urls_to_try.append(photo_url)
            
            # CRITICAL FIX: If URL contains non-numeric filename (e.g., "asier-osambela.png"),
            # try using player_id directly instead
            # Futmondo photos are typically named with numeric IDs: {player_id}.png
            if '/' in photo_url:
                filename = photo_url.split('/')[-1]
                # If filename is not numeric (contains letters/dashes), try player_id format
                if not filename.split('.')[0].isdigit():
                    # Try using player_id directly with common extensions
                    for ext in ['.png', '.jpg', '.jpeg']:
                        numeric_url = f"{base_url}/{player_id}{ext}"
                        if numeric_url not in urls_to_try:
                            urls_to_try.append(numeric_url)
        
        # Always try player_id directly as fallback (Futmondo photos are usually {player_id}.png)
        if not urls_to_try or not photo_url:
            for ext in ['.png', '.jpg', '.jpeg']:
                numeric_url = f"{base_url}/{player_id}{ext}"
                if numeric_url not in urls_to_try:
                    urls_to_try.append(numeric_url)
        
        # Try each URL until one works
        for attempt_url in urls_to_try:
            try:
                # Download photo with proper headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                    'Referer': 'https://app.futmondo.com/',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9',
                }
                
                response = requests.get(attempt_url, timeout=10, stream=True, headers=headers)
                response.raise_for_status()
                
                # Determine file extension from content type or URL
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    # Try to get extension from URL
                    ext = Path(attempt_url).suffix or '.png'
                
                local_path = self.photos_dir / f"{player_id}{ext}"
                
                # Save file
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = local_path.stat().st_size
                
                # Calculate hash
                file_hash = hashlib.md5()
                with open(local_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        file_hash.update(chunk)
                file_hash_str = file_hash.hexdigest()
                
                logger.info(f"Downloaded photo for player {player_id} from {attempt_url}: {local_path} ({file_size} bytes)")
                return str(local_path)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.debug(f"404 for {attempt_url}, trying next URL format...")
                    continue  # Try next URL
                else:
                    logger.warning(f"HTTP error {e.response.status_code} for {attempt_url}: {e}")
                    continue
            except Exception as e:
                logger.debug(f"Error downloading from {attempt_url}: {e}, trying next URL...")
                continue  # Try next URL
        
        # All URLs failed
        logger.error(f"Failed to download photo for player {player_id} from all attempted URLs: {urls_to_try}")
        return None
    
    def save_photo_metadata(self, player_id: str, photo_url: Optional[str], local_path: Optional[str], file_size: Optional[int] = None, file_hash: Optional[str] = None):
        """Save photo metadata to database"""
        if not local_path:
            return
        
        from datetime import datetime
        now = datetime.now().isoformat()
        
        # Calculate file size and hash if not provided
        if local_path and os.path.exists(local_path):
            if not file_size:
                file_size = os.path.getsize(local_path)
            
            if not file_hash:
                file_hash_obj = hashlib.md5()
                with open(local_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        file_hash_obj.update(chunk)
                file_hash = file_hash_obj.hexdigest()
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO player_photos 
                    (player_id, photo_url, local_path, downloaded_at, file_size, file_hash, last_checked)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id) DO UPDATE SET
                        photo_url = EXCLUDED.photo_url,
                        local_path = EXCLUDED.local_path,
                        downloaded_at = EXCLUDED.downloaded_at,
                        file_size = EXCLUDED.file_size,
                        file_hash = EXCLUDED.file_hash,
                        last_checked = EXCLUDED.last_checked
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO player_photos 
                    (player_id, photo_url, local_path, downloaded_at, file_size, file_hash, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
            
            cursor.execute(sql, (player_id, photo_url, local_path, now, file_size, file_hash, now))
    
    def get_photo_path(self, player_id: str) -> Optional[str]:
        """Get local photo path for a player - checks both DB and file system"""
        if not player_id:
            return None
        
        # First, try to find by database entry
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            sql = "SELECT local_path FROM player_photos WHERE player_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (player_id,))
            result = cursor.fetchone()
            
            if result and result[0] and os.path.exists(result[0]):
                return result[0]
        
        # Fallback: Try to find file directly in photos directory by player_id
        # Photos are saved as {player_id}.png, {player_id}.jpg, etc.
        for ext in ['.png', '.jpg', '.jpeg', '.webp']:
            photo_file = self.photos_dir / f"{player_id}{ext}"
            if photo_file.exists():
                logger.debug(f"Found photo by filename: {photo_file}")
                return str(photo_file)
        
        return None
    
    def process_player_photo(self, player_data: Dict, player_id: str) -> Optional[str]:
        """Process and download photo for a player - EFFICIENT: uses single DB connection for all operations"""
        # Check if photo already exists and is valid
        existing_path = self.get_photo_path(player_id)
        if existing_path:
            return existing_path
        
        # Extract photo URL
        photo_url = self.extract_photo_url(player_data)
        if not photo_url:
            logger.debug(f"No photo URL found for player {player_id}")
            return None
        
        # EFFICIENT: Use single connection for all DB operations
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # CRITICAL: Ensure player exists BEFORE downloading photo
            try:
                self._ensure_player_exists_with_connection(conn, cursor, player_data, player_id)
            except Exception as e:
                logger.error(f"Failed to ensure player {player_id} exists: {e}")
                return None
            
            # Download photo
            local_path = self.download_photo(photo_url, player_id)
            if not local_path:
                return None
            
            # Save metadata (player should exist now)
            file_size = os.path.getsize(local_path) if os.path.exists(local_path) else None
            try:
                self.save_photo_metadata_with_connection(conn, cursor, player_id, photo_url, local_path, file_size)
            except Exception as e:
                logger.error(f"Failed to save photo metadata for player {player_id}: {e}")
                return None
            
            # Update players table with photo info
            try:
                sql = "UPDATE players SET photo_url = ?, photo_local_path = ? WHERE id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (photo_url, local_path, player_id))
            except Exception as e:
                logger.debug(f"Could not update players table for player {player_id}: {e}")
                # Non-critical, photo is already saved
        
        return local_path
    
    def _ensure_player_exists_with_connection(self, conn, cursor, player_data: Dict, player_id: str):
        """Ensure player exists in players table using existing connection"""
        # Check if player exists
        sql = "SELECT player_id FROM players WHERE player_id = ?"
        sql = self.db.adapt_params(sql)
        cursor.execute(sql, (player_id,))
        exists = cursor.fetchone()
        
        if exists:
            return
        
        # Create player with minimal data
        from datetime import datetime
        now = datetime.now()
        
        player_name = player_data.get("name", "Unknown Player")
        
        if self.db.db_type in ["postgresql", "postgres"]:
            sql = '''
                INSERT INTO players (player_id, name, last_updated)
                VALUES (%s, %s, %s)
                ON CONFLICT (player_id) DO NOTHING
            '''
        else:
            sql = "INSERT OR IGNORE INTO players (player_id, name, last_updated) VALUES (?, ?, ?)"
        sql = self.db.adapt_params(sql)
        
        cursor.execute(sql, (player_id, player_name, now))
    
    def save_photo_metadata_with_connection(self, conn, cursor, player_id: str, photo_url: Optional[str], local_path: Optional[str], file_size: Optional[int] = None):
        """Save photo metadata using existing connection"""
        if not local_path:
            return
        
        from datetime import datetime
        now = datetime.now().isoformat()
        
        # Calculate file hash
        file_hash = None
        if local_path and os.path.exists(local_path):
            file_hash_obj = hashlib.md5()
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash_obj.update(chunk)
            file_hash = file_hash_obj.hexdigest()
        
        if self.db.db_type in ["postgresql", "postgres"]:
            sql = '''
                INSERT INTO player_photos 
                (player_id, photo_url, local_path, downloaded_at, file_size, file_hash, last_checked)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id) DO UPDATE SET
                    photo_url = EXCLUDED.photo_url,
                    local_path = EXCLUDED.local_path,
                    downloaded_at = EXCLUDED.downloaded_at,
                    file_size = EXCLUDED.file_size,
                    file_hash = EXCLUDED.file_hash,
                    last_checked = EXCLUDED.last_checked
            '''
        else:
            sql = '''
                INSERT OR REPLACE INTO player_photos 
                (player_id, photo_url, local_path, downloaded_at, file_size, file_hash, last_checked)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            sql = self.db.adapt_params(sql)
        
        cursor.execute(sql, (player_id, photo_url, local_path, now, file_size, file_hash, now))
    
    def _ensure_player_exists(self, player_data: Dict, player_id: str):
        """Ensure player exists in players table, create if not exists"""
        from datetime import datetime
        import logging
        logger_ensure = logging.getLogger(__name__)
        
        # First check if player exists
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Check if player exists
            sql = "SELECT player_id FROM players WHERE player_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (player_id,))
            exists = cursor.fetchone()
            
            if exists:
                logger_ensure.debug(f"Player {player_id} already exists in players table")
                return  # Player already exists, nothing to do
        
        # Player doesn't exist, create it in a separate transaction
        # Use a fresh connection to ensure transaction isolation
        logger_ensure.info(f"Creating player {player_id} in players table...")
        
        # Create player with minimal data - handle missing fields gracefully
        now = datetime.now().isoformat()
        name = player_data.get("name") or player_data.get("playerName") or "Unknown"
        role = player_data.get("role") or player_data.get("position") or "Unknown"
        # Try multiple possible keys for team
        team = (
            player_data.get("team") or 
            player_data.get("teamName") or 
            player_data.get("realTeamName") or 
            "Unknown"
        )
        current_value = player_data.get("value") or player_data.get("current_value") or 0
        current_points = player_data.get("points") or player_data.get("current_points") or 0
        
        # Ensure we have valid non-null values for NOT NULL columns
        if not name or name == "":
            name = f"Player_{player_id[:8]}"
        if not role or role == "":
            role = "Unknown"
        if not team or team == "":
            team = "Unknown"
        
        logger_ensure.debug(f"Player data: id={player_id}, name={name}, role={role}, team={team}, value={current_value}, points={current_points}")
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                # PostgreSQL: Use ON CONFLICT to handle race conditions
                insert_sql = '''
                    INSERT INTO players (player_id, name, role, real_team_name, last_updated)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (player_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        role = EXCLUDED.role,
                        real_team_name = EXCLUDED.real_team_name,
                        last_updated = EXCLUDED.last_updated
                '''
            else:
                # SQLite: Use INSERT OR REPLACE
                insert_sql = '''
                    INSERT OR REPLACE INTO players (player_id, name, role, real_team_name, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                '''
                insert_sql = self.db.adapt_params(insert_sql)
            
            try:
                cursor.execute(insert_sql, (player_id, name, role, team, now))
                
                # Commit the transaction to ensure player exists before inserting photo
                if self.db.db_type in ["postgresql", "postgres"]:
                    conn.commit()
                    logger_ensure.info(f"✅ Committed player {player_id} ({name}) to database")
                else:
                    conn.commit()
                
                logger_ensure.info(f"Created player {player_id} ({name}) in players table")
                
                # Verify player was created in a NEW connection (important for PostgreSQL)
                # This ensures we see the committed transaction
                import time
                time.sleep(0.1)  # Small delay to ensure commit is visible
                
                with self.db.get_connection() as verify_conn:
                    verify_cursor = self.db.get_cursor(verify_conn)
                    verify_sql = "SELECT player_id, name FROM players WHERE player_id = ?"
                    verify_sql = self.db.adapt_params(verify_sql)
                    verify_cursor.execute(verify_sql, (player_id,))
                    verified = verify_cursor.fetchone()
                    if verified:
                        logger_ensure.info(f"✅ Verified player {player_id} ({verified[1]}) exists in players table")
                    else:
                        logger_ensure.warning(f"⚠️ Player {player_id} was not visible after commit - may need to wait")
            except Exception as e:
                # If player was created by another process, verify it exists
                logger_ensure.error(f"❌ Could not create player {player_id}: {e}")
                if self.db.db_type in ["postgresql", "postgres"]:
                    try:
                        conn.rollback()
                    except:
                        pass
                
                # Double-check that player exists (may have been created by another process)
                with self.db.get_connection() as check_conn:
                    check_cursor = self.db.get_cursor(check_conn)
                    verify_sql = "SELECT player_id FROM players WHERE player_id = ?"
                    verify_sql = self.db.adapt_params(verify_sql)
                    check_cursor.execute(verify_sql, (player_id,))
                    verified = check_cursor.fetchone()
                    if verified:
                        logger_ensure.info(f"✅ Player {player_id} was created by another process")
                    else:
                        logger_ensure.error(f"❌ Player {player_id} does not exist and could not be created: {e}")
                        raise Exception(f"Cannot proceed: player {player_id} does not exist in players table. Error: {e}")

