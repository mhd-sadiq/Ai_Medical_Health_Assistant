#!/usr/bin/env python3
"""
Script to update database with PillReminder table
"""

from app import app, db, PillReminder

def update_database():
    """Update database with PillReminder table"""
    
    print("🔄 Updating Database with PillReminder Table")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Create all tables (this will add the new PillReminder table)
            db.create_all()
            print("✅ Database updated successfully!")
            
            # Check if PillReminder table exists
            try:
                result = db.session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pill_reminder'")
                if result.fetchone():
                    print("✅ PillReminder table created successfully!")
                else:
                    print("❌ PillReminder table not found!")
            except Exception as e:
                print(f"❌ Error checking PillReminder table: {e}")
            
            # List all tables
            result = db.session.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 All tables in database: {tables}")
            
        except Exception as e:
            print(f"❌ Error updating database: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎯 Database Update Complete!")
    print("\n📋 Next Steps:")
    print("1. Restart your Flask app (python app.py)")
    print("2. Test the new Pill Reminder functionality")
    print("3. Check admin dashboard for pill reminder data")
    
    return True

if __name__ == "__main__":
    update_database() 