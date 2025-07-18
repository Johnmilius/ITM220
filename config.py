# Path to your SQLite database file
DB_PATH = "gym_tracker.db"

# User table info
USER_TABLE = "user"
USER_COLUMNS = {
    "user_name": "TEXT",
    "email": "TEXT"
}

# Weight log table info (matches your schema: personal_weight)
USER_WEIGHT_TABLE = "user_weight_log"
USER_WEIGHT_COLUMNS = {
    "user_id": "INTEGER",
    "weight": "REAL",    # FLOAT values stored as REAL in SQLite
    "date": "TEXT"       # Dates stored as ISO strings (e.g., '2025-07-17')
}
