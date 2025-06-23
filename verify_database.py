#!/usr/bin/env python3
"""
Database verification script for ExerciseHistory table
"""

import sqlite3
import os
from datetime import datetime

def verify_database():
    """Verify the database structure and ExerciseHistory table"""
    
    print("🔍 Verifying Database Structure")
    print("=" * 50)
    
    # Check if database file exists
    db_path = os.path.join('instance', 'users.db')
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at: {db_path}")
        return
    
    print(f"✅ Database file found at: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if ExerciseHistory table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='exercise_history'
        """)
        
        if cursor.fetchone():
            print("✅ ExerciseHistory table exists")
            
            # Get table structure
            cursor.execute("PRAGMA table_info(exercise_history)")
            columns = cursor.fetchall()
            
            print("\n📋 ExerciseHistory table structure:")
            for col in columns:
                print(f"  • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
            
            # Check if table has any data
            cursor.execute("SELECT COUNT(*) FROM exercise_history")
            count = cursor.fetchone()[0]
            print(f"\n📊 ExerciseHistory records: {count}")
            
            if count > 0:
                # Show recent exercises
                cursor.execute("""
                    SELECT user_id, exercise_title, duration, timestamp 
                    FROM exercise_history 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                """)
                recent_exercises = cursor.fetchall()
                
                print("\n🕒 Recent exercises:")
                for exercise in recent_exercises:
                    user_id, title, duration, timestamp = exercise
                    print(f"  • User {user_id}: {title} ({duration}s) - {timestamp}")
            
        else:
            print("❌ ExerciseHistory table does not exist")
            print("💡 This might happen if the database was created before the model was added")
            print("   Try deleting the database file and restarting the Flask app")
        
        # Check other important tables
        print("\n🔍 Checking other tables:")
        tables_to_check = ['user', 'general_health_chat', 'diet_tips_chat', 'symptom_checker_chat', 'bmi_calculator_chat', 'blood_donor_chat']
        
        for table in tables_to_check:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table,))
            
            if cursor.fetchone():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            else:
                print(f"  ❌ {table}: table missing")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎯 Database Verification Complete!")
    print("\n📋 If ExerciseHistory table is missing:")
    print("1. Stop the Flask app (Ctrl+C)")
    print("2. Delete the instance/users.db file")
    print("3. Restart the Flask app (python app.py)")
    print("4. The table will be created automatically")

if __name__ == "__main__":
    verify_database() 