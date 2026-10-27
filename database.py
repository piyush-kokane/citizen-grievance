import sqlite3

DATABASE_NAME = "citizen_grievance.db"


def get_connection():
    """Connect to the SQLite database."""
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    """Create the tables needed for the grievance analytics project."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS wards (
        ward_id INTEGER PRIMARY KEY,
        ward_name TEXT NOT NULL,
        population INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS departments (
        department_id INTEGER PRIMARY KEY,
        department_name TEXT NOT NULL,
        sla_days INTEGER DEFAULT 7
    );

    CREATE TABLE IF NOT EXISTS citizens (
        citizen_id INTEGER PRIMARY KEY,
        citizen_name TEXT,
        ward_id INTEGER,
        FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
    );

    CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY,
        staff_name TEXT,
        department_id INTEGER,
        FOREIGN KEY (department_id)
            REFERENCES departments(department_id)
    );

    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id INTEGER PRIMARY KEY,
        citizen_id INTEGER,
        ward_id INTEGER,
        department_id INTEGER,
        complaint_text TEXT,
        category TEXT,
        status TEXT DEFAULT 'Open',
        created_at TEXT,
        resolved_at TEXT,
        priority TEXT DEFAULT 'Medium',
        FOREIGN KEY (citizen_id) REFERENCES citizens(citizen_id),
        FOREIGN KEY (ward_id) REFERENCES wards(ward_id),
        FOREIGN KEY (department_id)
            REFERENCES departments(department_id)
    );

    CREATE TABLE IF NOT EXISTS status_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER,
        old_status TEXT,
        new_status TEXT,
        changed_at TEXT,
        FOREIGN KEY (complaint_id)
            REFERENCES complaints(complaint_id)
    );

    CREATE TABLE IF NOT EXISTS reassignments (
        reassignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER,
        old_department_id INTEGER,
        new_department_id INTEGER,
        reassigned_at TEXT,
        FOREIGN KEY (complaint_id)
            REFERENCES complaints(complaint_id)
    );

    CREATE TABLE IF NOT EXISTS resolutions (
        resolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER,
        resolution_text TEXT,
        resolution_days REAL,
        FOREIGN KEY (complaint_id)
            REFERENCES complaints(complaint_id)
    );

    CREATE TABLE IF NOT EXISTS text_features (
        feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER UNIQUE,
        cleaned_text TEXT,
        word_count INTEGER,
        FOREIGN KEY (complaint_id)
            REFERENCES complaints(complaint_id)
    );

    CREATE TABLE IF NOT EXISTS duplicate_pairs (
        pair_id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id_1 INTEGER,
        complaint_id_2 INTEGER,
        similarity REAL,
        FOREIGN KEY (complaint_id_1)
            REFERENCES complaints(complaint_id),
        FOREIGN KEY (complaint_id_2)
            REFERENCES complaints(complaint_id)
    );
    """)

    connection.commit()
    connection.close()

    print("Database and 10 tables created successfully.")


if __name__ == "__main__":
    create_tables()
