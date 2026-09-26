"""
Reset Database endpoint - Recreates database schema optimized for historical analysis
"""

import logging
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.services.data_initializer_v2 import DataInitializerV2
from app.services.data_manager_v2 import DataManagerV2

logger = logging.getLogger(__name__)

router = APIRouter()


def _db_admin_enabled() -> bool:
    """True solo si los endpoints destructivos de BD están habilitados.

    NFR1.2: `/api/v1/database/reset` y `/populate` recrean o borran el esquema.
    Deben estar protegidos tras un flag de entorno/admin y devolver 404 por
    defecto (no revelar su existencia). Valores aceptados: 1/true/yes/on.
    """
    return os.getenv("ENABLE_DB_ADMIN", "").strip().lower() in {"1", "true", "yes", "on"}


def _require_db_admin() -> None:
    """Bloquea el acceso salvo que ENABLE_DB_ADMIN esté activo.

    Devuelve 404 por defecto para no exponer la existencia del endpoint
    destructivo (NFR1.2 — proteger tras flag admin/env).
    """
    if not _db_admin_enabled():
        raise HTTPException(status_code=404, detail="Not Found")


@router.post("/reset")
async def reset_database(
    background_tasks: BackgroundTasks,
    populate_data: bool = False
):
    """Reset database to optimized schema for historical championship analysis

    WARNING: This will delete all existing data and recreate the schema.
    Protegido tras ENABLE_DB_ADMIN (NFR1.2): 404 por defecto.

    Args:
        populate_data: If True, will also populate database with fresh data after reset
        background_tasks: FastAPI background tasks
    """
    _require_db_admin()
    try:
        # Create DataManagerV2 without initializing database first
        # (reset_database will handle initialization)
        dm = DataManagerV2(skip_init=True)
        dm.reset_database()
        
        if populate_data:
            # Start data population in background
            def populate():
                try:
                    initializer = DataInitializerV2()
                    results = initializer.initialize_all_data(force_refresh=True)
                    logger.info(f"Data population complete: {results}")
                except Exception as e:
                    logger.error(f"Data population failed: {e}")
            
            background_tasks.add_task(populate)
            return {
                "status": "success",
                "message": "Database reset complete. Data population started in background.",
                "populate_data": True
            }
        else:
            return {
                "status": "success",
                "message": "Database reset complete. New optimized schema created for historical analysis.",
                "populate_data": False
            }
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/populate")
async def populate_database(
    force_refresh: bool = True
):
    """Populate database with data from all API endpoints

    Protegido tras ENABLE_DB_ADMIN (NFR1.2): 404 por defecto.

    Args:
        force_refresh: If True, bypasses cache and fetches fresh data
    """
    _require_db_admin()
    try:
        initializer = DataInitializerV2()
        results = initializer.initialize_all_data(force_refresh=force_refresh)
        return {
            "status": "complete",
            "results": results
        }
    except Exception as e:
        logger.error(f"Data population failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

