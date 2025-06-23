#!/usr/bin/env python3
"""
Script to recreate the database with all tables including exercise_history
"""

import os
import shutil
from datetime import datetime

def recreate_database():
    """Recreate the database with all tables"""
    
    print("🔄 Recreating Database with All Tables")
    print("=" * 50)
    
    # Backup existing database
    db_path = 'instance/users.db'
    backup_path = 'instance/users_backup.db'
    
    if os.path.exists(db_path):
        print(f"📦 Backing up existing database to {backup_path}")
        shutil.copy2(db_path, backup_path)
        print("✅ Backup created successfully")
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Removed old database")
    
    # Import Flask app and create new database
    try:
        from app import app, db
        
        with app.app_context():
            print("🔨 Creating new database with all tables...")
            db.create_all()
            print("✅ Database created successfully!")
            
            # Verify tables were created
            from app import User, ExerciseHistory, GeneralHealthChat, DietTipsChat, SymptomCheckerChat, BMICalculatorChat, BloodDonorChat, BloodDonor, LoginHistory
            
            # Check if exercise_history table exists
            try:
                # Try to query the table to see if it exists
                result = db.session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise_history'")
                if result.fetchone():
                    print("✅ exercise_history table created successfully!")
                else:
                    print("❌ exercise_history table still missing!")
            except Exception as e:
                print(f"❌ Error checking exercise_history table: {e}")
            
            # List all tables
            result = db.session.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 All tables in database: {tables}")
            
            # Create a test admin user
            try:
                admin_user = User(
                    name="Admin User",
                    email="admin@example.com",
                    is_admin=True,
                    is_superuser=True
                )
                admin_user.set_password("admin123")
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Created test admin user (admin@example.com / admin123)")
            except Exception as e:
                print(f"⚠️ Could not create admin user: {e}")
            
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 Database Recreation Complete!")
    print("\n📋 Next Steps:")
    print("1. Restart your Flask app (python app.py)")
    print("2. Test exercise logging functionality")
    print("3. Check admin dashboard for exercise history")
    print("\n🔑 Test Admin Login:")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    
    return True

if __name__ == "__main__":
    recreate_database() 