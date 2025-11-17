from dotenv import load_dotenv
import os
import logging

# Load .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration - PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/codeshield')

# Database pool configuration
DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "10"))
DB_POOL_MIN_IDLE = int(os.getenv("DB_POOL_MIN_IDLE", "1"))
DB_POOL_IDLE_TIMEOUT = int(os.getenv("DB_POOL_IDLE_TIMEOUT", "30000"))
DB_POOL_MAX_LIFETIME = int(os.getenv("DB_POOL_MAX_LIFETIME", "1800000"))
DB_POOL_CONNECTION_TIMEOUT = int(os.getenv("DB_POOL_CONNECTION_TIMEOUT", "30000"))
DB_POOL_NAME = os.getenv("DB_POOL_NAME", "CodeShieldAI")

# Redis Configuration for caching
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "password": os.getenv("REDIS_PASSWORD", ""),
    "ttl": int(os.getenv("REDIS_TTL", 300)),
    "namespace": os.getenv("REDIS_NAMESPACE", "codeshield"),
    "timeout": int(os.getenv("REDIS_TIMEOUT_MS", 10000)),
    "pool": {
        "max_active": int(os.getenv("REDIS_MAX_ACTIVE", 20)),
        "max_idle": int(os.getenv("REDIS_MAX_IDLE", 5)),
        "min_idle": int(os.getenv("REDIS_MIN_IDLE", 1))
    }
}

# Application Configuration
APP_ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "codeshield-secret-key-2025-production-ready")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "debug").upper()

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
CORS_METHODS = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
CORS_HEADERS = os.getenv("CORS_HEADERS", "*").split(",")

# Google Gemini API Configuration
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY", ""),
    "model": os.getenv("GEMINI_MODEL", "gemini-pro"),
    "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "8192")),
}

# Security Configuration
SECURITY_CONFIG = {
    "max_code_length": int(os.getenv("MAX_CODE_LENGTH", "50000")),  # 50KB max
    "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "10")),
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "log_file_path": os.getenv("LOG_FILE_PATH", "logs/app.log"),
    "log_max_size": int(os.getenv("LOG_MAX_SIZE", "10485760")),  # 10MB
    "log_backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5")),
}

# Development Configuration
DEV_CONFIG = {
    "reload": os.getenv("RELOAD", "true").lower() == "true",
    "host": os.getenv("HOST", "0.0.0.0"),
    "port": int(os.getenv("PORT", "8000")),
    "workers": int(os.getenv("WORKERS", "1")),
}

# Configuration validation
def validate_config():
    """Validate critical configuration values"""
    errors = []
    
    if not GEMINI_CONFIG["api_key"]:
        errors.append("GEMINI_API_KEY must be set in environment variables")
    
    if SECRET_KEY == "codeshield-secret-key-2025-production-ready" and APP_ENV == "production":
        errors.append("SECRET_KEY must be changed from default value in production")
    
    if APP_ENV == "production" and DEBUG:
        errors.append("DEBUG should be False in production")
    
    if errors:
        logger.warning("Configuration validation warnings:")
        for error in errors:
            logger.warning(f"  - {error}")
    
    return len(errors) == 0

# Validate configuration on import
validate_config()


