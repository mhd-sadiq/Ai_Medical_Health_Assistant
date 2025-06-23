import sqlite3
import os

# Check database
db_path = 'instance/users.db'
if os.path.exists(db_path):
    print(f"Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check if exercise_history table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise_history'")
    if cursor.fetchone():
        print("\n✅ exercise_history table exists!")
        
        # Check table structure
        cursor.execute("PRAGMA table_info(exercise_history)")
        columns = cursor.fetchall()
        print("Table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check if there's any data
        cursor.execute("SELECT COUNT(*) FROM exercise_history")
        count = cursor.fetchone()[0]
        print(f"\nRecords in exercise_history: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM exercise_history ORDER BY timestamp DESC LIMIT 3")
            records = cursor.fetchall()
            print("Recent records:")
            for record in records:
                print(f"  - {record}")
    else:
        print("\n❌ exercise_history table does NOT exist!")
        print("This is why exercises aren't being saved.")
    
    conn.close()
else:
    print(f"Database not found: {db_path}") 