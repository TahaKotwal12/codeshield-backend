#!/usr/bin/env python3
"""
Startup script for CodeShield AI Backend Server

This script starts the FastAPI server on port 8000.
"""

import uvicorn
import sys
import os
from app.config.logger import get_logger
from app.config.config import DEV_CONFIG

logger = get_logger(__name__)

def start_server():
    """Start the FastAPI server."""
    try:
        logger.info("Starting CodeShield AI Backend Server...")
        logger.info(f"Server will be available at: http://localhost:{DEV_CONFIG['port']}")
        logger.info("Health check: http://localhost:8000/health")
        logger.info("API docs: http://localhost:8000/docs")
        logger.info("Analyze endpoint: POST http://localhost:8000/api/v1/analyze")
        logger.info("")
        logger.info("Press Ctrl+C to stop the server.")
        logger.info("=" * 60)
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=DEV_CONFIG["host"],
            port=DEV_CONFIG["port"],
            reload=DEV_CONFIG["reload"],
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()


