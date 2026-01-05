import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ======================
# TABLE USERS
# ======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# ======================
# TABLE SERVICES
# ======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER
)
""")

# ======================
# TABLE JOBS
# ======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    service_id INTEGER,
    employee_id INTEGER,
    date TEXT,
    status TEXT
)
""")

# ======================
# TABLE ATTENDANCE
# ======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    service_id INTEGER,
    status TEXT,
    date TEXT,
    comment TEXT
)
""")

# ======================
# ADMIN PAR DÉFAUT
# ======================
cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role)
VALUES ('admin', 'admin123', 'admin')
""")

# 🔒 COMMIT À LA FIN
conn.commit()
conn.close()

print("✅ Base de données créée avec succès")

cursor.execute("""
ALTER TABLE jobs ADD COLUMN photo_before TEXT
""")

cursor.execute("""
ALTER TABLE jobs ADD COLUMN photo_after TEXT
""")

cursor.execute("""
ALTER TABLE jobs ADD COLUMN employee_note TEXT
""")
