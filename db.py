import logging
import mysql.connector
from config import Config

logger = logging.getLogger(__name__)


def get_connection():
    """Create and return an active MySQL database connection."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        connect_timeout=5,
    )


def test_connection():
    """
    Test MySQL connection and return (success: bool, safe_message: str).
    Ensures credentials and sensitive host details are never returned to callers.
    """
    try:
        conn = get_connection()
        if conn.is_connected():
            server_info = getattr(conn, "server_info", None) or conn.get_server_info()
            conn.close()
            return True, f"Connected to MySQL Server {server_info}"
        return False, "Database connection could not be established."
    except Exception as error:
        # Log technical error securely on the server
        logger.error("Database connection probe failed: %s", type(error).__name__)
        return False, f"Database service unreachable ({type(error).__name__})."
