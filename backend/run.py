#!/usr/bin/env python3
"""
Run script for Futmondo API backend
"""

import uvicorn
from app.core.config import API_HOST, API_PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )







