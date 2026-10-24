import os
from dotenv import load_dotenv

# Load local environment configuration if available
load_dotenv()


class Config:
    """Application configuration with secure defaults and environment overrides."""

    # Flask Settings - Debug mode is FALSE by default for safety
    SECRET_KEY = os.getenv("SECRET_KEY", "student-performance-system-secure-key-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", "5000"))

    # Database Settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "student_performance")

    # Academic & Analysis Settings
    ACADEMIC_SUPPORT_THRESHOLD = float(os.getenv("SUPPORT_THRESHOLD", "40.0"))
    DEFAULT_TOP_N = int(os.getenv("TOP_N", "3"))
    # Supported: AVERAGE (average of assessments per subject), BEST (highest score), LATEST
    ASSESSMENT_AGGREGATION = os.getenv("ASSESSMENT_AGGREGATION", "AVERAGE").upper()

    # File Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_CHARTS_DIR = os.path.join(BASE_DIR, "static", "charts")
