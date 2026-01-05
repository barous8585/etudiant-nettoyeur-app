import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def add_column_if_not_exists(column_name, sql):
    try:
        cursor.execute(sql)
        print(f"✅ Colonne '{column_name}' ajoutée")
    except sqlite3.OperationalError:
        print(f"ℹ️ Colonne '{column_name}' existe déjà")

# PHOTO AVANT
add_column_if_not_exists(
    "photo_before",
    "ALTER TABLE jobs ADD COLUMN photo_before TEXT"
)

# PHOTO APRÈS
add_column_if_not_exists(
    "photo_after",
    "ALTER TABLE jobs ADD COLUMN photo_after TEXT"
)

# COMMENTAIRE EMPLOYÉ
add_column_if_not_exists(
    "employee_note",
    "ALTER TABLE jobs ADD COLUMN employee_note TEXT"
)

conn.commit()
conn.close()

print("🚀 Migration des preuves terminée")
