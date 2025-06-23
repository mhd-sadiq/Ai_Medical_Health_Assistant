import sqlite3

db_path = 'instance/users.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column already exists
cursor.execute("PRAGMA table_info(pill_reminder)")
columns = [col[1] for col in cursor.fetchall()]

if 'exact_time' not in columns:
    try:
        cursor.execute("ALTER TABLE pill_reminder ADD COLUMN exact_time TIME")
        print("✅ exact_time column added to pill_reminder table.")
    except Exception as e:
        print("⚠️", e)
else:
    print("ℹ️ exact_time column already exists.")

conn.commit()
conn.close()
print("Done.") 