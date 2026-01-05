import sqlite3
from security import hash_password

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute(
    "UPDATE users SET password=? WHERE username='admin'",
    (hash_password("admin123"),)
)

conn.commit()
conn.close()
print("✅ Mot de passe admin sécurisé")
